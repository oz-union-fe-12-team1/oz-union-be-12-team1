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
    return user   # ✅ 이미 UserOut 반환


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

    return updated_user   # ✅ 이미 UserUpdateResponse 반환


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

    return deleted   # ✅ UserService에서 UserDeleteResponse 반환
