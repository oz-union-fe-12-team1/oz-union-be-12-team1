from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
from passlib.hash import bcrypt

from core.config import settings
from repositories.user_repo import UserRepository
from repositories.token_revocations_repo import TokenRevocationsRepository
from models.user import User


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
    async def register(email: str, password: str, nickname: str) -> Optional[User]:
        password_hash = bcrypt.hash(password)

        verification_token = jwt.encode(
            {"email": email, "exp": datetime.utcnow() + timedelta(hours=1)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        user = await UserRepository.create_user(
            email=email,
            password_hash=password_hash,
            nickname=nickname,
        )

        # 토큰 저장 (Tortoise 모델은 await 필요)
        user.verification_token = verification_token
        user.is_verified = False
        await user.save()

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

        if not user.is_verified:
            return {"error": "EMAIL_NOT_VERIFIED"}

        access_token = AuthService.create_access_token(user.id)
        refresh_token = AuthService.create_refresh_token(user.id)

        # 로그인 기록 갱신
        user.login_count = (user.login_count or 0) + 1
        user.last_login_ip = "TODO: 클라이언트 IP"
        await user.save()

        return {"access_token": access_token, "refresh_token": refresh_token}

    # ---------------------------
    # 이메일 인증 (/auth/email/verify)
    # ---------------------------
    @staticmethod
    async def verify_email_token(email: str, token: str) -> Dict:
        user = await UserRepository.get_user_by_email(email)
        if not user or not user.verification_token:
            return {"success": False, "error": "TOKEN_INVALID"}

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("email") != user.email:
                return {"success": False, "error": "TOKEN_INVALID"}

            user.is_verified = True
            user.verification_token = None
            await user.save()
            return {"success": True}
        except jwt.ExpiredSignatureError:
            return {"success": False, "error": "TOKEN_EXPIRED"}
        except jwt.InvalidTokenError:
            return {"success": False, "error": "TOKEN_INVALID"}

    # ---------------------------
    # 구글 로그인 (/auth/google)
    # ---------------------------
    @staticmethod
    async def google_login(google_id: str, email: str, nickname: str) -> Dict[str, str]:
        """
        ⚠️ 실제 구현에서는 Google OAuth API 검증 필요.
        여기서는 social_provider='google' 로직만 반영.
        """
        user = await UserRepository.get_user_by_email(email)

        if not user:
            user = await UserRepository.create_user(
                email=email,
                password_hash=bcrypt.hash("oauth_dummy_password"),  # 구글 계정은 내부 PW 필요 없음
                nickname=nickname,
                social_provider="google",
                social_id=google_id,
            )
            user.is_verified = True
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

            # 블랙리스트 확인
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
        return await TokenRevocationsRepository.revoke_token(token)
