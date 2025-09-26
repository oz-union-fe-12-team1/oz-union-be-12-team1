from typing import Optional, List
from tortoise.exceptions import DoesNotExist
from datetime import date
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
        birthday: date,
    ) -> User:
        """회원가입"""
        user = await User.create(
            email=email,
            password_hash=password_hash,
            username=username,
            birthday=birthday,
            is_email_verified=False,  # ✅ 기본: 인증 전
        )
        return user

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        """ID 기준 단일 조회"""
        try:
            return await User.get(id=user_id)
        except DoesNotExist:
            return None

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """이메일 기준 단일 조회"""
        return await User.filter(email=email).first()

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        """이름 기준 단일 조회"""
        return await User.filter(username=username).first()

    @staticmethod
    async def get_all_users() -> List[User]:
        """관리자 전용 전체 사용자 조회"""
        return await User.all().order_by("-created_at")

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def verify_user(user_id: int) -> Optional[User]:
        """이메일 인증 완료 → is_email_verified=True 로 변경"""
        user = await User.get_or_none(id=user_id)
        if not user:
            return None
        user.is_email_verified = True   # ✅ 명세서 기준 필드
        await user.save()
        return user

    @staticmethod
    async def update_profile(
        user_id: int,
        username: Optional[str] = None,
        bio: Optional[str] = None,
        profile_image: Optional[str] = None,
    ) -> Optional[User]:
        """프로필 수정 (username, bio, profile_image)"""
        user = await User.get_or_none(id=user_id)
        if not user:
            return None

        if username is not None:
            user.username = username
        if bio is not None:
            user.bio = bio
        if profile_image is not None:  # ✅ 사진이 들어왔을 때만 업데이트
            user.profile_image = profile_image

        await user.save()
        return user

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """회원 탈퇴"""
        user = await User.get_or_none(id=user_id)
        if not user:
            return False
        await user.delete()
        return True

