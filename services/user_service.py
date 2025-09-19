from typing import Optional, List
from repositories.user_repo import UserRepository
from models.user import User


class UserService:
    """
    Service layer for managing Users (CRUD + 인증/프로필 관리).
    """

    # --------------------
    # CREATE
    # --------------------
    @staticmethod
    async def create_user(
        email: str,
        password_hash: str,
        username: str,
        birthday: str,   # ✅ 완료테이블 기준 반영
    ) -> User:
        """회원가입"""
        return await UserRepository.create_user(
            email=email,
            password_hash=password_hash,
            username=username,
            birthday=birthday,
        )

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
    async def get_all_users() -> List[User]:
        """전체 유저 목록 (관리자 전용)"""
        return await UserRepository.get_all_users()

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def verify_user(user_id: int) -> Optional[User]:
        """이메일 인증 처리"""
        return await UserRepository.verify_user(user_id)

    @staticmethod
    async def update_profile(user_id: int, name: Optional[str] = None,
                             bio: Optional[str] = None,
                             profile_image: Optional[str] = None) -> Optional[User]:
        """프로필 수정 (명세서 기준)"""
        return await UserRepository.update_profile(
            user_id,
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
