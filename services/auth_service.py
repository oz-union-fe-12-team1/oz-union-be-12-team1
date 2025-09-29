from datetime import datetime, timedelta, date
from typing import Optional, Any
import jwt
import random   # 인증번호 및 토큰 생성용
import redis.asyncio as redis
from passlib.hash import bcrypt
import httpx

from core.config import settings
from models.token_revocations import TokenRevocation
from repositories.user_repo import UserRepository
from core.security import send_verification_email
from repositories.token_revocations_repo import TokenRevocationsRepository
from models.user import User
from schemas.user import UserCreateRequest

# Redis 연결 (docker-compose 기준 redis 컨테이너)
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
    # 이메일 인증번호 발송
    # ---------------------------
    @staticmethod
    async def send_verification_email_code(email: str) -> dict[str, Any]:
        existing = await UserRepository.get_user_by_email(email)
        if existing:
            return {"success": False, "error": "EMAIL_ALREADY_EXISTS"}

        code = str(random.randint(100000, 999999))
        await redis_client.set(f"verify:{email}", code, ex=600)
        await send_verification_email(email, code)
        return {"success": True}

    # ---------------------------
    # 이메일 인증번호 검증
    # ---------------------------
    @staticmethod
    async def verify_email_code(email: str, code: str) -> dict[str, Any]:
        saved_code = await redis_client.get(f"verify:{email}")
        if not saved_code:
            return {"success": False, "error": "TOKEN_EXPIRED"}
        if saved_code != code:
            return {"success": False, "error": "TOKEN_INVALID"}

        existing = await UserRepository.get_user_by_email(email)
        if existing and existing.is_email_verified:
            return {"success": False, "error": "ALREADY_VERIFIED"}

        await redis_client.set(f"verify:success:{email}", "true", ex=600)
        await redis_client.delete(f"verify:{email}")
        return {"success": True}

    # ---------------------------
    # 회원가입
    # ---------------------------
    @staticmethod
    async def register(request: UserCreateRequest) -> dict[str, Any] | None:
        verified = await redis_client.get(f"verify:success:{request.email}")
        if not verified:
            return {"success": False, "error": "EMAIL_NOT_VERIFIED"}

        existing = await UserRepository.get_user_by_email(request.email)
        if existing:
            return {"success": False, "error": "EMAIL_ALREADY_EXISTS"}

        password_hash = bcrypt.hash(request.password)
        user = await UserRepository.create_user(
            email=request.email,
            password_hash=password_hash,
            username=request.username,
            birthday=request.birthday,
        )
        user.is_email_verified = False
        await user.save()
        return {"success": True}

    # ---------------------------
    # 로그인
    # ---------------------------
    @staticmethod
    async def login(email: str, password: str) -> dict[str, Any]:
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
    # 비밀번호 재설정 요청
    # ---------------------------
    @staticmethod
    async def request_password_reset(email: str) -> dict[str, Any]:
        user = await UserRepository.get_user_by_email(email)
        if not user:
            return {"success": False, "error": "USER_NOT_FOUND"}

        token = str(random.randint(100000, 999999))
        await redis_client.set(f"pwd_reset:{email}", token, ex=600)

        # TODO: 실제 메일 발송 구현 필요
        # await send_verification_email(email, token)

        return {"success": True}

    # ---------------------------
    # 비밀번호 재설정 확인
    # ---------------------------
    @staticmethod
    async def confirm_password_reset(email: str, token: str, new_password: str) -> dict[str, Any]:
        saved = await redis_client.get(f"pwd_reset:{email}")
        if not saved or saved != token:
            return {"success": False, "error": "INVALID_OR_EXPIRED_TOKEN"}

        user = await UserRepository.get_user_by_email(email)
        if not user:
            return {"success": False, "error": "USER_NOT_FOUND"}

        user.password_hash = bcrypt.hash(new_password)
        await user.save()
        await redis_client.delete(f"pwd_reset:{email}")
        return {"success": True}

    # ---------------------------
    # 구글 로그인 콜백
    # ---------------------------
    @staticmethod
    async def google_callback(code: str) -> dict[str, Any]:
        try:
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(token_url, data=data)
                token_data = resp.json()
                if "error" in token_data:
                    raise Exception(f"Google token error: {token_data}")

                access_token = token_data["access_token"]
                userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
                headers = {"Authorization": f"Bearer {access_token}"}
                user_response = await client.get(userinfo_url, headers=headers)
                if user_response.status_code != 200:
                    raise Exception(f"userinfo error: {user_response.text}")
                info = user_response.json()
                name = info.get("name")
                email = info.get("email")
                google_id = info.get("sub")

            user = await UserRepository.get_user_by_email(email)
            if not user:
                user = await UserRepository.create_user(
                    email=email,
                    password_hash="",
                    username=name or "구글사용자",
                    birthday=date(2000, 1, 1),
                )
                user.google_id = google_id
                user.is_email_verified = True
                await user.save()

            access_token = AuthService.create_access_token(user.id)
            refresh_token = AuthService.create_refresh_token(user.id)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }

        except Exception as e:
            raise Exception(f"Google OAuth error: {e}")

    # ---------------------------
    # 토큰 갱신
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
    # 로그아웃
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
