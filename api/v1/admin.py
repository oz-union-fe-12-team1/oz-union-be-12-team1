from typing import Optional
from schemas.user import (
    UserCreateRequest,
    UserCreateResponse,
    UserOut,
    UserUpdateRequest,
    UserUpdateResponse,
    UserDeleteResponse,
    AdminUserOut,
    UserListResponse,
    AdminUserListResponse,
)
from repositories.user_repo import UserRepository


class UserService:
    """
    Service layer for managing Users (CRUD + 관리자 기능).
    인증/로그인은 AuthService에서 담당.
    """

    # --------------------
    # CREATE (회원가입)
    # --------------------
    @staticmethod
    async def create_user(data: UserCreateRequest) -> UserCreateResponse:
        user = await UserRepository.create_user(
            email=data.email,
            password_hash=data.password,  # ✅ 실제로는 AuthService에서 해시 후 전달
            username=data.username,
            birthday=data.birthday,
        )
        return UserCreateResponse.model_validate(user, from_attributes=True)

    # --------------------
    # READ (내 정보 / 단일 조회)
    # --------------------
    @staticmethod
    async def get_user_by_id(user_id: int, admin: bool = False):
        user = await UserRepository.get_user_by_id(user_id)
        if not user:
            return None
        if admin:
            return AdminUserOut.model_validate(user, from_attributes=True)
        return UserOut.model_validate(user, from_attributes=True)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[UserOut]:
        user = await UserRepository.get_user_by_email(email)
        if not user:
            return None
        return UserOut.model_validate(user, from_attributes=True)

    # --------------------
    # READ (목록 조회)
    # --------------------
    @staticmethod
    async def get_all_users(admin: bool = False):
        users = await UserRepository.get_all_users()
        if admin:
            return AdminUserListResponse(
                users=[AdminUserOut.model_validate(u, from_attributes=True) for u in users],
                total=len(users),
            )
        return UserListResponse(
            users=[UserOut.model_validate(u, from_attributes=True) for u in users],
            total=len(users),
        )

    # --------------------
    # UPDATE (프로필 수정)
    # --------------------
    @staticmethod
    async def update_profile(user_id: int, data: UserUpdateRequest) -> Optional[UserUpdateResponse]:
        updated = await UserRepository.update_profile(
            user_id=user_id,
            username=data.username,
            bio=data.bio,
            profile_image=data.profile_image,
        )
        if not updated:
            return None
        return UserUpdateResponse.model_validate(updated, from_attributes=True)

    # --------------------
    # 관리자 전용: 사용자 상태 변경
    # --------------------
    @staticmethod
    async def update_user_status(user_id: int, is_active: bool) -> Optional[AdminUserOut]:
        user = await UserRepository.get_user_by_id(user_id)
        if not user:
            return None
        user.is_active = is_active
        await user.save()
        return AdminUserOut.model_validate(user, from_attributes=True)  # ✅ 통일

    # --------------------
    # DELETE (회원 탈퇴 / 관리자 삭제)
    # --------------------
    @staticmethod
    async def delete_user(user_id: int) -> Optional[UserDeleteResponse]:
        deleted = await UserRepository.delete_user(user_id)
        if not deleted:
            return None
        return UserDeleteResponse(message="User deleted successfully")  # ✅ 통일
