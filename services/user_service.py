from typing import Optional, List
from schemas.users import (
    UserCreateRequest,
    UserCreateResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserOut,
    UserUpdateRequest,
    UserUpdateResponse,
    UserDeleteResponse,
    UserListResponse,
)
from repositories.user_repo import UserRepository
from models.user import User
from utils.security import hash_password, verify_password, create_tokens


class UserService:
    """
    Service layer for managing Users (CRUD + 인증/로그인).
    """

    # --------------------
    # CREATE
    # --------------------
    @staticmethod
    async def create_user(data: UserCreateRequest) -> UserCreateResponse:
        password_hash: str = hash_password(data.password)
        user: User = await UserRepository.create_user(
            email=data.email,
            password_hash=password_hash,
            username=data.username,
            birthday=data.birthday,
        )
        return UserCreateResponse.model_validate(user, from_attributes=True)

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[UserOut]:
        user: Optional[User] = await UserRepository.get_user_by_id(user_id)
        if not user:
            return None
        return UserOut.model_validate(user, from_attributes=True)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[UserOut]:
        user: Optional[User] = await UserRepository.get_user_by_email(email)
        if not user:
            return None
        return UserOut.model_validate(user, from_attributes=True)

    @staticmethod
    async def get_all_users() -> UserListResponse:
        users: List[User] = await UserRepository.get_all_users()
        return UserListResponse(
            users=[UserOut.model_validate(u, from_attributes=True) for u in users],
            total=len(users),
        )

    # --------------------
    # LOGIN
    # --------------------
    @staticmethod
    async def login_user(data: UserLoginRequest) -> Optional[UserLoginResponse]:
        user: Optional[User] = await UserRepository.get_user_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash or ""):
            return None

        access_token, refresh_token = create_tokens(user.id)
        return UserLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def update_profile(user_id: int, data: UserUpdateRequest) -> Optional[UserUpdateResponse]:
        updated: Optional[User] = await UserRepository.update_profile(
            user_id=user_id,
            username=data.username,
            bio=data.bio,
            profile_image=data.profile_image,
        )
        if not updated:
            return None
        return UserUpdateResponse.model_validate(updated, from_attributes=True)

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_user(user_id: int) -> Optional[UserDeleteResponse]:
        deleted: bool = await UserRepository.delete_user(user_id)
        if not deleted:
            return None
        return UserDeleteResponse(message="User deleted successfully")
