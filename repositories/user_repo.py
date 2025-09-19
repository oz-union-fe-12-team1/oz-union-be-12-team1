from typing import Optional, List
from tortoise.exceptions import DoesNotExist
from models.user import User


class UserRepository:
    """
    Repository for managing User data (CRUD + 인증 관련 조회).
    """

    # --------------------
    # CREATE
    # --------------------
    @staticmethod
    async def create_user(
        email: str,
        password_hash: str,
        username: str,
        birthday: str,
    ) -> User:
        """회원가입"""
        user = await User.create(
            email=email,
            password_hash=password_hash,
            username=username,
            birthday=birthday,
            is_verified=False,  # ✅ 기본: 인증 전
        )
        return user

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        try:
            return await User.get(id=user_id)
        except DoesNotExist:
            return None

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        try:
            return await User.get(email=email)
        except DoesNotExist:
            return None

    @staticmethod
    async def get_all_users() -> List[User]:
        """관리자 전용 전체 사용자 조회"""
        return await User.all().order_by("-created_at")
