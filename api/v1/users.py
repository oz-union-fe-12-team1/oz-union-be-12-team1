from fastapi import APIRouter, Depends, HTTPException
from schemas.user import (
    UserCreateResponse,   # ✅ 조회 시 재활용
    UserUpdateRequest,
    UserUpdateResponse,
    UserDeleteResponse,
)
from services.user_service import UserService
from models.user import User
from core.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

# -----------------------------
# 내 프로필 조회
# -----------------------------
@router.get("/me", response_model=UserCreateResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)) -> UserCreateResponse:
    return UserCreateResponse.model_validate(current_user)

# -----------------------------
# 내 프로필 수정
# -----------------------------
@router.put("/me", response_model=UserUpdateResponse)
async def update_my_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
) -> UserUpdateResponse:
    updated_user = await UserService.update_profile(
        user_id=current_user.id,
        username=request.username,
        bio=request.bio,
        profile_image=request.profile_image,
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return UserUpdateResponse.model_validate(updated_user)

# -----------------------------
# 회원 탈퇴
# -----------------------------
@router.delete("/me", response_model=UserDeleteResponse)
async def delete_my_account(current_user: User = Depends(get_current_user)) -> UserDeleteResponse:
    deleted = await UserService.delete_user(current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return UserDeleteResponse(success=True)
