from typing import Optional, List
from repositories.user_repo import UserRepository
from models.user import User


class UserService:
    """
    Service layer for managing Users
    (조회, 프로필 관리, 회원 탈퇴, 관리자 기능).
    """

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        """ID 기준 단일 유저 조회"""
        return await UserRepository.get_user_by_id(user_id)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """이메일 기준 단일 유저 조회"""
        return await UserRepository.get_user_by_email(email)

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        """이메일 기준 단일 유저 조회"""
        return await UserRepository.get_user_by_username(username)

    @staticmethod
    async def get_all_users() -> List[User]:
        """전체 유저 목록 (관리자 전용)"""
        return await UserRepository.get_all_users()

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def update_profile(
        user_id: int,
        username: Optional[str] = None,
        bio: Optional[str] = None,
        profile_image: Optional[str] = None
    ) -> Optional[User]:
        """프로필 수정 (마이페이지)"""
        return await UserRepository.update_profile(
            user_id=user_id,
            username=username,
            bio=bio,
            profile_image=profile_image
        )

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """회원 탈퇴"""
        return await UserRepository.delete_user(user_id)

    # ---------------------------
    # 관리자(Admin) 전용 메서드
    # ---------------------------
    @staticmethod
    async def update_user_status(user_id: int, is_active: bool) -> Optional[User]:
        """사용자 활성/비활성 상태 변경"""
        user = await User.get_or_none(id=user_id)
        if user:
            user.is_active = is_active
            await user.save()
        return user

    @staticmethod
    async def set_superuser(user_id: int, is_superuser: bool) -> Optional[User]:
        """관리자 권한 부여/회수"""
        user = await User.get_or_none(id=user_id)
        if user:
            user.is_superuser = is_superuser
            await user.save()
        return user
