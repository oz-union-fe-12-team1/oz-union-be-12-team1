from datetime import datetime, timedelta, date
from typing import Optional
import jwt
import random
import redis.asyncio as redis
from passlib.hash import bcrypt

from core.config import settings
from repositories.user_repo import UserRepository
from core.security import send_verification_email
from repositories.token_revocations_repo import TokenRevocationsRepository
from models.user import User
from schemas.users import (  # ✅ 경로 일관성 (schemas.user → schemas.users)
    UserCreateRequest,
    UserCreateResponse,
    UserLoginResponse,
    GoogleLoginResponse,
    UserVerifySuccessResponse,
)

# ✅ Redis 연결
REDIS_URL: str = "redis://redis:6379/0"
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


class AuthService:
    """
    Authentication & Authorization Service
    (회원가입/로그인/토큰/인증)
    """

    # ---------------------------
    # JWT 토큰 발급
    # ---------------------------
    @staticmethod
    def create_access_token(user_id: int) -> str:
        expire: datetime = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload: dict[str, str | datetime] = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        expire: datetime = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        payload: dict[str, str | datetime] = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # ---------------------------
    # 회원가입 (/auth/register)
    # ---------------------------
    @staticmethod
    async def register(request: UserCreateRequest) -> UserCreateResponse:
        password_hash: str = bcrypt.hash(request.password)

        # 인증번호 생성 (6자리)
        verification_code: str = str(random.randint(100000, 999999))

        # 유저 생성
        user: User = await UserRepository.create_user(
            email=request.email,
            password_hash=password_hash,
            username=request.username,
            birthday=request.birthday,
        )
        user.is_email_verified = False
        await user.save()

        # Redis에 인증번호 저장 (10분 TTL)
        await redis_client.set(f"verify:{request.email}", verification_code, ex=600)

        # 이메일 발송
        await send_verification_email(request.email, verification_code)

        return UserCreateResponse.model_validate(user, from_attributes=True)

    # ---------------------------
    # 로그인 (/auth/login)
    # ---------------------------
    @staticmethod
    async def login(email: str, password: str) -> Optional[UserLoginResponse]:
        user: Optional[User] = await UserRepository.get_user_by_email(email)
        if not user or not user.password_hash:
            return None

        if not bcrypt.verify(password, user.password_hash):
            return None

        if not user.is_email_verified:
            return None

        access_token: str = AuthService.create_access_token(user.id)
        refresh_token: str = AuthService.create_refresh_token(user.id)

        # 로그인 기록 갱신
        user.last_login_at = datetime.utcnow()
        await user.save()

        return UserLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    # ---------------------------
    # 이메일 인증 (/auth/email/verify)
    # ---------------------------
    @staticmethod
    async def verify_email_token(email: str, code: str) -> UserVerifySuccessResponse:
        saved_code: Optional[str] = await redis_client.get(f"verify:{email}")
        if not saved_code or saved_code != code:
            return UserVerifySuccessResponse(success=False)

        user: Optional[User] = await UserRepository.get_user_by_email(email)
        if not user:
            return UserVerifySuccessResponse(success=False)

        user.is_email_verified = True
        await user.save()

        # 인증번호 삭제
        await redis_client.delete(f"verify:{email}")

        return UserVerifySuccessResponse(success=True)

    # ---------------------------
    # 구글 로그인 (/auth/google)
    # ---------------------------
    @staticmethod
    async def google_login(google_id: str, email: str) -> GoogleLoginResponse:
        user: Optional[User] = await UserRepository.get_user_by_email(email)

        if not user:
            # 신규 사용자 생성
            user = await UserRepository.create_user(
                email=email,
                password_hash=bcrypt.hash("oauth_dummy_password"),
                username="소셜유저",
                birthday=date(2000, 1, 1),
            )
            user.social_provider = "google"
            user.social_id = google_id
            user.is_email_verified = True
            await user.save()

        access_token: str = AuthService.create_access_token(user.id)
        refresh_token: str = AuthService.create_refresh_token(user.id)

        return GoogleLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    # ---------------------------
    # 토큰 갱신 (/auth/refresh)
    # ---------------------------
    @staticmethod
    async def refresh_token(refresh_token: str) -> Optional[UserLoginResponse]:
        try:
            payload: dict = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id: int = int(payload.get("sub"))

            if await TokenRevocationsRepository.is_token_revoked(refresh_token):
                return None

            new_access: str = AuthService.create_access_token(user_id)
            return UserLoginResponse(
                access_token=new_access,
                refresh_token=refresh_token,
                token_type="bearer",
            )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

    # ---------------------------
    # 로그아웃 (/auth/logout)
    # ---------------------------
    @staticmethod
    async def logout(token: str) -> bool:
        try:
            payload: dict = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id: int = int(payload.get("sub"))

            jti: str = token  # 여기선 토큰 자체를 JTI처럼 사용
            return await TokenRevocationsRepository.revoke_token(jti, user_id)

        except jwt.InvalidTokenError:
            return False
