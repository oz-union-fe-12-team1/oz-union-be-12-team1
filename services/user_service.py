from typing import Optional, List
from passlib.hash import bcrypt
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
        update_data = {}
        user = await UserRepository.get_user_by_id(user_id)
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

    @staticmethod
    async def change_password(
        user: User,
        old_password: str,
        new_password: str,
        new_password_check: str,
    ) -> dict[str, bool | str]:
        if not bcrypt.verify(old_password, user.password_hash):
            return {"success": False, "error": "WRONG_OLD_PASSWORD"}

        if new_password != new_password_check:
            return {"success": False, "error": "PASSWORD_MISMATCH"}

        user.password_hash = bcrypt.hash(new_password)
        await user.save()
        return {"success": True}
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
