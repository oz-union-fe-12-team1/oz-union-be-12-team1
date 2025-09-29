from datetime import datetime, timedelta, date
from typing import Optional, Dict
import jwt
import random   #  인증번호 생성용
import redis.asyncio as redis   #  Redis 클라이언트
from passlib.hash import bcrypt
import httpx

from core.config import settings
from models.token_revocations import TokenRevocation
from repositories.user_repo import UserRepository
from core.security import send_verification_email   #  메일 발송 함수
from repositories.token_revocations_repo import TokenRevocationsRepository
from models.user import User
from schemas.user import UserCreateRequest

#  Redis 연결 (docker-compose 기준 redis 컨테이너)
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
        user.is_email_verified = False   #  완료테이블 기준 반영
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

        user.is_email_verified = True   #  완료테이블 기준 반영
        await user.save()

        # 인증번호 삭제 (1회성)
        await redis_client.delete(f"verify:{email}")

        return {"success": True}

    # ---------------------------
    # 구글 로그인 (/auth/google/callback)
    # ---------------------------
    @staticmethod
    async def google_callback(code: str) -> dict[str, str]:
        print(f"=== AuthService.google_callback 시작: code={code[:30]}...")  # ⭕
        try:
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            print("Google token request data:", data)

            print(">>> httpx.AsyncClient 생성 중...")  # ⭕
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(">>> POST 요청 시작...")  # ⭕
                resp = await client.post(token_url, data=data)
                print(f">>> 응답 받음! status_code={resp.status_code}")  # ⭕
                print("Google token raw response:", resp.text)

                token_data = resp.json()
                if "error" in token_data:
                    print(f">>> 구글 토큰 오류: {token_data}")  # ⭕
                    raise Exception(f"Google token error: {token_data}")

                access_token = token_data["access_token"]
                print(f">>> access_token 획득 성공: {access_token[:20]}...")  # ⭕

                # (2) userinfo 가져오기
                userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
                headers = {"Authorization": f"Bearer {access_token}"}
                print(">>> userinfo 요청 중...")  # ⭕
                user_response = await client.get(userinfo_url, headers=headers)
                print(f">>> userinfo 응답: status={user_response.status_code}")  # ⭕

                if user_response.status_code != 200:
                    raise Exception(f"userinfo error: {user_response.text}")

                info = user_response.json()
                print("Google userinfo response:", info)

                name = info.get("name")
                email = info.get("email")
                google_id = info.get("sub")

            print(">>> DB 작업 시작...")  # ⭕
            # (3) DB 조회 또는 신규 생성
            user = await UserRepository.get_user_by_email(email)
            if not user:
                print(f">>> 신규 사용자 생성: {email}")  # ⭕
                user = await UserRepository.create_user(
                    email=email,
                    password_hash="",
                    username=name or "구글사용자",
                    birthday=date(2000, 1, 1),
                )
                user.google_id = google_id
                user.is_email_verified = True
                await user.save()

            print(">>> JWT 발급 중...")  # ⭕
            # (4) JWT 발급
            access_token = AuthService.create_access_token(user.id)
            refresh_token = AuthService.create_refresh_token(user.id)

            result = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
            print(f">>> 완료! 반환값: {result.keys()}")  # ⭕
            return result

        except httpx.TimeoutException as e:
            print(f"❌ 타임아웃: {e}")
            raise Exception(f"Google API timeout: {e}")
        except httpx.RequestError as e:
            print(f"❌ 네트워크 오류: {e}")
            raise Exception(f"Network error: {e}")
        except Exception as e:
            print(f"❌ Google OAuth error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
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
            user_id = int(payload.get("sub"))   #  sub → user_id

            #  jti는 토큰 전체 문자열로 저장
            jti = token

            #  repository에 jti와 user_id 전달
            return await TokenRevocationsRepository.revoke_token(jti, user_id)
        except jwt.InvalidTokenError:
            return None