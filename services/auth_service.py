from datetime import datetime, timedelta, date
from typing import Optional, Dict
import jwt
import random   # ✅ 인증번호 생성용
import redis.asyncio as redis   # ✅ Redis 클라이언트
from passlib.hash import bcrypt
import httpx
from google.oauth2 import id_token
import requests


from core.config import settings
from models.token_revocations import TokenRevocation
from repositories.user_repo import UserRepository
from core.security import send_verification_email   # ✅ 메일 발송 함수
from repositories.token_revocations_repo import TokenRevocationsRepository
from models.user import User
from schemas.user import UserCreateRequest, GoogleCallbackResponse

# ✅ Redis 연결 (docker-compose 기준 redis 컨테이너)
REDIS_URL = "redis://redis:6379/0"
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


class AuthService:
    """
    Authentication & Authorization service.
    API 명세서 + 완료테이블 기반 (Tortoise ORM 맞춤형)
    """

    # ---------------------------
    # JWT 토큰 발급
    # ---------------------------
    @staticmethod
    def create_access_token(user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # ---------------------------
    # 회원가입 (/auth/register)
    # ---------------------------
    @staticmethod
    async def register(request: UserCreateRequest) -> User:
        """유저 생성 + 인증번호 발송"""
        password_hash = bcrypt.hash(request.password)

        # 인증번호(6자리) 생성
        verification_code = str(random.randint(100000, 999999))

        # 유저 생성
        user = await UserRepository.create_user(
            email=request.email,
            password_hash=password_hash,
            username=request.username,
            birthday=request.birthday,
        )
        user.is_email_verified = False   # ✅ 완료테이블 기준 반영
        await user.save()

        # Redis에 인증번호 저장 (10분 TTL)
        await redis_client.set(f"verify:{request.email}", verification_code, ex=600)

        # 이메일 발송
        await send_verification_email(request.email, verification_code)

        return user

    # ---------------------------
    # 로그인 (/auth/login)
    # ---------------------------
    @staticmethod
    async def login(email: str, password: str) -> Dict[str, str]:
        user = await UserRepository.get_user_by_email(email)
        if not user:
            return {"error": "USER_NOT_FOUND"}

        if not bcrypt.verify(password, user.password_hash):
            return {"error": "INVALID_CREDENTIALS"}

        if not user.is_email_verified:   # ✅ 수정됨
            return {"error": "EMAIL_NOT_VERIFIED"}

        access_token = AuthService.create_access_token(user.id)
        refresh_token = AuthService.create_refresh_token(user.id)

        # 로그인 기록 갱신
        user.last_login_ip = "TODO: 클라이언트 IP"
        await user.save()

        return {"access_token": access_token, "refresh_token": refresh_token}

    # ---------------------------
    # 이메일 인증 (/auth/email/verify)
    # ---------------------------
    @staticmethod
    async def verify_email_token(email: str, code: str) -> Dict:
        saved_code = await redis_client.get(f"verify:{email}")
        if not saved_code:
            return {"success": False, "error": "CODE_EXPIRED_OR_NOT_FOUND"}

        if saved_code != code:
            return {"success": False, "error": "CODE_MISMATCH"}

        user = await UserRepository.get_user_by_email(email)
        if not user:
            return {"success": False, "error": "USER_NOT_FOUND"}

        user.is_email_verified = True   # ✅ 완료테이블 기준 반영
        await user.save()

        # 인증번호 삭제 (1회성)
        await redis_client.delete(f"verify:{email}")

        return {"success": True}

    # ---------------------------
    # 구글 로그인 (/auth/google/callback)
    # ---------------------------
    @staticmethod
    async def google_callback(code: str) -> dict[str, str]:
        try:
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }

            # 1. 구글에 access_token + id_token 요청
            async with httpx.AsyncClient() as client:
                resp = await client.post(token_url, data=data)
                # token_data = resp.json()

                access_token = resp.json()['access_token']
                user_info = f"https://www.googleapis.com/oauth2/v1/userinfo"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                }
                user_response = requests.get(user_info, headers=headers)


                if user_response.status_code != 200:
                    raise Exception

        except:
            raise Exception("google oauth error")

        info = user_response.json()
        name=info.get('name')
        email=info.get('email')
        google_id=info.get('id_token')
        print(name, email, google_id)

        # if "id_token" not in token_data:
        #     raise Exception("GOOGLE_TOKEN_INVALID")

        # # 2. id_token 검증 → 사용자 정보 추출
        # idinfo = id_token.verify_oauth2_token(
        #     token_data["id_token"],
        #     requests.Request(),
        #     settings.GOOGLE_CLIENT_ID,
        # )
        #
        # google_id = idinfo["sub"]
        # email = idinfo["email"]
        # name = idinfo.get("name")

        # 3. DB 조회 (기존 유저 여부 확인)
        user = await UserRepository.get_user_by_email(email)
        if not user:
            # 신규 사용자 생성
            user = await UserRepository.create_user(
                email=email,
                password_hash="",  # 소셜 로그인은 비밀번호 불필요
                username=name or "구글사용자",
                birthday=date(2000, 1, 1),  # 기본값
            )
            user.google_id = google_id
            user.is_email_verified = True
            await user.save()

        # 4. JWT 토큰 발급
        access_token = AuthService.create_access_token(user.id)
        refresh_token = AuthService.create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    # ---------------------------
    # 토큰 갱신 (/auth/refresh)
    # ---------------------------
    @staticmethod
    async def refresh_token(refresh_token: str) -> Optional[str]:
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = int(payload.get("sub"))

            if await TokenRevocationsRepository.is_token_revoked(refresh_token):
                return None

            return AuthService.create_access_token(user_id)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    # ---------------------------
    # 로그아웃 (/auth/logout)
    # ---------------------------
    @staticmethod
    async def logout(token: str) -> Optional[TokenRevocation]:
        try:
            # ✅ 토큰 디코드해서 user_id 추출
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id = int(payload.get("sub"))   # ✅ sub → user_id

            # ✅ jti는 토큰 전체 문자열로 저장
            jti = token

            # ✅ repository에 jti와 user_id 전달
            return await TokenRevocationsRepository.revoke_token(jti, user_id)

        except jwt.InvalidTokenError:
            return None