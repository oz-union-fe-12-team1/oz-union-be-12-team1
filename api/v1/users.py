from fastapi import APIRouter, Depends, HTTPException
from schemas.user import (
    UserOut,
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
@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    로그인한 사용자 본인의 프로필 조회
    """
    user = await UserService.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return UserOut.model_validate(user, from_attributes=True)  # ✅ 명시적으로 스키마 변환


# -----------------------------
# 내 프로필 수정
# -----------------------------
@router.put("/me", response_model=UserUpdateResponse)
async def update_my_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    """
    로그인한 사용자 본인의 프로필 수정
    """
    updated_user = await UserService.update_profile(
        user_id=current_user.id,
        data=request,
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")

    return UserUpdateResponse.model_validate(updated_user, from_attributes=True)  # ✅ 변환


# -----------------------------
# 회원 탈퇴
# -----------------------------
@router.delete("/me", response_model=UserDeleteResponse)
async def delete_my_account(current_user: User = Depends(get_current_user)):
    """
    로그인한 사용자 본인 계정 삭제
    """
    deleted = await UserService.delete_user(current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")

    return UserDeleteResponse(message="User deleted successfully")  # ✅ 명확히 스키마 생성
