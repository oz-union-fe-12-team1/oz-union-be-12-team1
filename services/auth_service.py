from datetime import datetime, timedelta, date
from typing import Optional, Dict
import jwt
import random   # ✅ 인증번호 생성용
import redis.asyncio as redis   # ✅ Redis 클라이언트
from passlib.hash import bcrypt

from core.config import settings
from repositories.user_repo import UserRepository
from core.security import send_verification_email   # ✅ 메일 발송 함수
from repositories.token_revocations_repo import TokenRevocationsRepository
from models.user import User


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
    async def register(request) -> Optional[User]:
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
    async def login(email: str, password: str) -> Optional[Dict[str, str]]:
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
    # 구글 로그인 (/auth/google)
    # ---------------------------
    @staticmethod
    async def google_login(google_id: str, email: str) -> Dict[str, str]:
        user = await UserRepository.get_user_by_email(email)

        if not user:
            user = await UserRepository.create_user(
                email=email,
                password_hash=bcrypt.hash("oauth_dummy_password"),
                social_provider="google",
                social_id=google_id,
            )
            user.is_email_verified = True
            await user.save()

        access_token = AuthService.create_access_token(user.id)
        refresh_token = AuthService.create_refresh_token(user.id)

        return {"access_token": access_token, "refresh_token": refresh_token}

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
    async def logout(token: str) -> bool:
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
            return False