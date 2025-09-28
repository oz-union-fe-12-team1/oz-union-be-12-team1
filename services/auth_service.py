from datetime import datetime, timedelta, date
from typing import Optional, Dict
import jwt
import random   # ✅ 인증번호 생성용
import redis.asyncio as redis
from passlib.hash import bcrypt

from core.config import settings
from models.token_revocations import TokenRevocation
from repositories.user_repo import UserRepository
from core.security import send_verification_email   # ✅ 메일 발송 함수
from repositories.token_revocations_repo import TokenRevocationsRepository
from models.user import User
from schemas.user import UserCreateRequest

# ✅ Redis 연결
REDIS_URL = "redis://redis:6379/0"
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


class AuthService:
    """
    Authentication & Authorization service.
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
    # 이메일 인증 메일 발송 (/auth/email/verify_code)
    # ---------------------------
    @staticmethod
    async def send_verification_email_code(email: str) -> Dict:
        """이메일 입력 → 인증번호 생성 & 발송"""
        existing = await UserRepository.get_user_by_email(email)
        if existing:
            return {"success": False, "error": "EMAIL_ALREADY_EXISTS"}

        code = str(random.randint(100000, 999999))

        # Redis에 저장 (10분 TTL)
        await redis_client.set(f"verify:{email}", code, ex=600)

        # 이메일 발송
        await send_verification_email(email, code)

        return {"success": True}

    # ---------------------------
    # 인증 번호 확인 (/auth/email/verify)
    # ---------------------------
    @staticmethod
    async def verify_email_code(email: str, code: str) -> Dict:
        """Redis에 저장된 코드 검증"""
        saved_code = await redis_client.get(f"verify:{email}")
        if not saved_code:
            return {"success": False, "error": "TOKEN_EXPIRED"}  # 400

        if saved_code != code:
            return {"success": False, "error": "TOKEN_INVALID"}  # 400

        # 이미 인증된 경우 방어
        existing = await UserRepository.get_user_by_email(email)
        if existing and existing.is_email_verified:
            return {"success": False, "error": "ALREADY_VERIFIED"}  # 409

        # 너무 자주 요청 시 rate limit 체크 (추가 로직 가능)
        # 지금은 스킵, 필요시 구현

        # 성공 → 가입 가능 플래그 저장
        await redis_client.set(f"verify:success:{email}", "true", ex=600)
        await redis_client.delete(f"verify:{email}")

        return {"success": True}

    # ---------------------------
    # 회원가입 (/auth/register)
    # ---------------------------
    @staticmethod
    async def register(request: UserCreateRequest) -> Optional[User]:
        """이메일 인증을 마친 사용자만 DB에 가입"""
        verified = await redis_client.get(f"verify:success:{request.email}")
        if not verified:
            return None  # EMAIL_NOT_VERIFIED

        existing = await UserRepository.get_user_by_email(request.email)
        if existing:
            return None  # EMAIL_ALREADY_EXISTS

        password_hash = bcrypt.hash(request.password)

        user = await UserRepository.create_user(
            email=request.email,
            password_hash=password_hash,
            username=request.username,
            birthday=request.birthday,
        )

        # 가입 후 플래그 제거
        await redis_client.delete(f"verify:success:{request.email}")

        return user
    #----------------------------
    # 비밀번호 재설정 /auth/password/reset-request, /auth/password/reset-confirm
    #----------------------------
    @staticmethod
    async def request_password_reset(email: str) -> dict[str, bool|str]:
        user = await UserRepository.get_user_by_email(email)
        if not user:
            return {"success": False}
        return {"success": True}

    @staticmethod
    async def confirm_password_reset(email: str, new_password: str, new_password_check: str) -> dict[str, bool]:
        """비밀번호 재설정: 새 비밀번호 저장"""
        if new_password != new_password_check:
            return {"success": False}

        user = await UserRepository.get_user_by_email(email)
        if not user:
            return {"success": False}

        user.password_hash = bcrypt.hash(new_password)
        await user.save()

        return {"success": True}
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

        if not user.is_email_verified:
            return {"error": "EMAIL_NOT_VERIFIED"}

        access_token = AuthService.create_access_token(user.id)
        refresh_token = AuthService.create_refresh_token(user.id)

        user.last_login_ip = "TODO: 클라이언트 IP"
        await user.save()

        return {"access_token": access_token, "refresh_token": refresh_token}
    # ---------------------------
    # 구글 로그인 (/auth/google/callback)
    # ---------------------------
    # @staticmethod
    # async def google_callback(code: str) -> dict[str, str]:
    #     try:
    #         token_url = "https://oauth2.googleapis.com/token"
    #         data = {
    #             "code": code,
    #             "client_id": settings.GOOGLE_CLIENT_ID,
    #             "client_secret": settings.GOOGLE_SECRET,
    #             "redirect_uri": settings.GOOGLE_REDIRECT_URI,
    #             "grant_type": "authorization_code",
    #         }
    #
    #         # 1. 구글에 access_token + id_token 요청
    #         async with httpx.AsyncClient() as client:
    #             resp = await client.post(token_url, data=data)
    #             # token_data = resp.json()
    #
    #             access_token = resp.json()['access_token']
    #             user_info = f"https://www.googleapis.com/oauth2/v1/userinfo"
    #             headers = {
    #                 "Authorization": f"Bearer {access_token}",
    #             }
    #             user_response = requests.get(user_info, headers=headers)
    #
    #
    #             if user_response.status_code != 200:
    #                 raise Exception
    #
    #     except:
    #         raise Exception("google oauth error")
    #
    #     info = user_response.json()
    #     name=info.get('name')
    #     email=info.get('email')
    #     google_id=info.get('id_token')
    #     print(name, email, google_id)
    #
    #     # if "id_token" not in token_data:
    #     #     raise Exception("GOOGLE_TOKEN_INVALID")
    #     #
    #     # # 2. id_token 검증 → 사용자 정보 추출
    #     # idinfo = id_token.verify_oauth2_token(
    #     #     token_data["id_token"],
    #     #     requests.Request(),
    #     #     settings.GOOGLE_CLIENT_ID,
        # )
        #
        # google_id = idinfo["sub"]
        # email = idinfo["email"]
        # name = idinfo.get("name")

        # # 3. DB 조회 (기존 유저 여부 확인)
        # user = await UserRepository.get_user_by_email(email)
        # if not user:
        #     # 신규 사용자 생성
        #     user = await UserRepository.create_user(
        #         email=email,
        #         password_hash="",  # 소셜 로그인은 비밀번호 불필요
        #         username=name or "구글사용자",
        #         birthday=date(2000, 1, 1),  # 기본값
        #     )
        #     user.google_id = google_id
        #     user.is_email_verified = True
        #     await user.save()
        #
        # # 4. JWT 토큰 발급
        # access_token = AuthService.create_access_token(user.id)
        # refresh_token = AuthService.create_refresh_token(user.id)
        #
        # return {
        #     "access_token": access_token,
        #     "refresh_token": refresh_token,
        #     "token_type": "bearer",
        # }

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
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = int(payload.get("sub"))
            jti = token
            return await TokenRevocationsRepository.revoke_token(jti, user_id)
        except jwt.InvalidTokenError:
            return None