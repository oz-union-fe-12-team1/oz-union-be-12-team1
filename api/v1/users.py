from fastapi import APIRouter, Depends, HTTPException
from schemas.user import (
    UserOut,
    UserUpdateRequest,
    UserUpdateResponse,
    UserDeleteResponse,
)
from services.user_service import UserService
from models.user import User
from core.security import get_current_user   # ✅ core/security.py 의 인증 유틸 사용

router = APIRouter(prefix="/users", tags=["users"])

# -----------------------------
# 내 프로필 조회
# -----------------------------
@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: User = Depends(get_current_user)) -> UserOut:
    """
    로그인한 사용자 본인의 프로필 조회
    """
    return UserOut.model_validate(
        current_user)


# -----------------------------
# 내 프로필 수정
# -----------------------------
@router.put("/me", response_model=UserUpdateResponse)
async def update_my_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
) -> UserUpdateResponse:
    """
    로그인한 사용자 본인의 프로필 수정
    """
    updated_user = await UserService.update_profile(
        user_id=current_user.id,
        username=request.username,
        bio=request.bio,
        profile_image=request.profile_image,
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")

    return UserUpdateResponse.model_validate(updated_user)   # ✅ 스키마 매핑 통일


# -----------------------------
# 회원 탈퇴
# -----------------------------
@router.delete("/me", response_model=UserDeleteResponse)
async def delete_my_account(current_user: User = Depends(get_current_user)) -> UserDeleteResponse:
    """
    로그인한 사용자 본인 계정 삭제
    """
    deleted = await UserService.delete_user(current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")

    return UserDeleteResponse(message="User deleted successfully")  # ✅ 응답 스키마 통일
