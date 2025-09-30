from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any
import jwt
import random   # ✅ 인증번호 생성용
import redis.asyncio as redis
from passlib.hash import bcrypt
import httpx

from core.config import settings
from models.token_revocations import TokenRevocation
from repositories.user_repo import UserRepository
from core.verify_mail import send_verification_email   # ✅ 메일 발송 함수
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
    #분실 시 재설정을 위한 이메일 확인
    @staticmethod
    async def request_password_reset(email: str) -> dict[str, bool | str]:
        user = await UserRepository.get_user_by_email(email)
        if not user:
            return {"success": False, "error": "USER_NOT_FOUND"}
        return {"success": True}

    @staticmethod
    async def confirm_password_reset(
        email: str,
        new_password: str,
        new_password_check: str
    ) -> dict[str, bool | str]:
        """비밀번호 재설정: 새 비밀번호 저장"""
        if new_password != new_password_check:
            return {"success": False, "error": "PASSWORD_MISMATCH"}

        user = await UserRepository.get_user_by_email(email)
        if not user:
            return {"success": False, "error": "USER_NOT_FOUND"}

        # 비밀번호 해싱 후 저장
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