from typing import Optional, List
from tortoise.exceptions import DoesNotExist
from models.user import User


class UserRepository:
    """
    Repository for managing User data (CRUD + 인증 관련 조회).
    """

    # ✅ Create (회원가입)
    @staticmethod
    async def create_user(
        email: str,
        password_hash: str,
        nickname: str,
        name: Optional[str] = None,
        birth_date: Optional[str] = None,
        phone: Optional[str] = None,
        profile_image: Optional[str] = None,
        bio: Optional[str] = None,
        social_provider: Optional[str] = None,
        social_id: Optional[str] = None,
    ) -> User:
        user = await User.create(
            email=email,
            password_hash=password_hash,
            nickname=nickname,
            name=name,
            birth_date=birth_date,
            phone=phone,
            profile_image=profile_image,
            bio=bio,
            social_provider=social_provider,
            social_id=social_id,
            is_verified=False,  # 이메일 인증 전 기본값
        )
        return user

    # ✅ Read (단일 유저 조회 by ID)
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        try:
            return await User.get(id=user_id)
        except DoesNotExist:
            return None

    # ✅ Read (단일 유저 조회 by Email)
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        try:
            return await User.get(email=email)
        except DoesNotExist:
            return None

    # ✅ Read (닉네임 중복 검사)
    @staticmethod
    async def is_nickname_taken(nickname: str) -> bool:
        return await User.filter(nickname=nickname).exists()

    # ✅ Update (이메일 인증 처리)
    @staticmethod
    async def verify_user(user_id: int) -> Optional[User]:
        try:
            user = await User.get(id=user_id)
            user.is_verified = True
            await user.save()
            return user
        except DoesNotExist:
            return None

    # ✅ Update (프로필 수정)
    @staticmethod
    async def update_profile(user_id: int, **kwargs) -> Optional[User]:
        """
        kwargs: nickname, name, phone, profile_image, bio 등
        """
        try:
            user = await User.get(id=user_id)
            for field, value in kwargs.items():
                setattr(user, field, value)
            await user.save()
            return user
        except DoesNotExist:
            return None

    # ✅ Delete (사용자 탈퇴)
    @staticmethod
    async def delete_user(user_id: int) -> bool:
        deleted_count = await User.filter(id=user_id).delete()
        return deleted_count > 0

    # ✅ Read (전체 사용자 목록 - 관리자용)
    @staticmethod
    async def get_all_users() -> List[User]:
        return await User.all().order_by("-created_at")
