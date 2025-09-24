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
        """
        회원가입
        - 신규 가입자는 기본적으로 이메일 미인증 상태
        """
        return await User.create(
            email=email,
            password_hash=password_hash,
            username=username,
            birthday=birthday,
            is_email_verified=False,  # ✅ 명세서: 가입 직후 인증되지 않음
        )

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        """ID 기준 단일 조회"""
        return await User.get_or_none(id=user_id)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """이메일 기준 단일 조회"""
        return await User.get_or_none(email=email)

    @staticmethod
    async def get_all_users() -> List[User]:
        """
        전체 사용자 목록 조회 (관리자 전용)
        - 최근 가입순 정렬
        """
        return await User.all().order_by("-created_at")

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def verify_user(user_id: int) -> Optional[User]:
        """
        이메일 인증 완료 → is_email_verified = True
        """
        user = await User.get_or_none(id=user_id)
        if not user:
            return None
        user.is_email_verified = True
        await user.save()
        return user

    @staticmethod
    async def update_profile(
        user_id: int,
        username: Optional[str] = None,
        bio: Optional[str] = None,
        profile_image: Optional[str] = None,
    ) -> Optional[User]:
        """
        프로필 수정
        - username, bio, profile_image 중 선택적 업데이트
        """
        user = await User.get_or_none(id=user_id)
        if not user:
            return None

        if username is not None:
            user.username = username
        if bio is not None:
            user.bio = bio
        if profile_image is not None:
            user.profile_image = profile_image

        await user.save()
        return user

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """
        회원 탈퇴
        - 실제 DB에서 삭제
        - 복구 불가
        """
        deleted_count = await User.filter(id=user_id).delete()
        return deleted_count > 0
