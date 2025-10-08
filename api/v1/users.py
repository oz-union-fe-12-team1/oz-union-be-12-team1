from fastapi import APIRouter, Depends, HTTPException
from mypyc.crash import crash_report

from schemas.user import (
    UserCreateResponse,  # ✅ 조회 시 재활용
    UserUpdateRequest,
    UserUpdateResponse,
    UserDeleteResponse,
    UserVerifySuccessResponse,
    PasswordChangeRequest, UserOut,
)
from services.user_service import UserService
from models.user import User
from core.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

# -----------------------------
# 내 프로필 조회
# -----------------------------
@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(
        {
            **current_user.__dict__,
            "is_google_user": bool(current_user.google_id)
        },
        from_attributes=True,
    )

# -----------------------------
# 내 프로필 수정
# -----------------------------
@router.patch("/me", response_model=UserUpdateResponse)
async def update_my_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
) -> UserUpdateResponse:
    updated_user = await UserService.update_profile(
        user_id=current_user.id,
        username=request.username,
        bio=request.bio,
        profile_image=request.profile_image,
        birthday=request.birthday,
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return UserUpdateResponse.model_validate(updated_user)

#비밀번호 변경
@router.post(
    "/password/change",
    response_model=UserVerifySuccessResponse,
)
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    result = await UserService.change_password(
        user=current_user,
        old_password=request.old_password,
        new_password=request.new_password,
        new_password_check=request.new_password_check,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return {"success": True}

# -----------------------------
# 회원 탈퇴
# -----------------------------
@router.delete("/me", response_model=UserDeleteResponse)
async def delete_my_account(current_user: User = Depends(get_current_user)) -> UserDeleteResponse:
    deleted = await UserService.delete_user(current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return UserDeleteResponse(success=True)
