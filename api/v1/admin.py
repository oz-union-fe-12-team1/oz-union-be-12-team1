from fastapi import APIRouter, HTTPException, Depends

from models.user import User
from services.user_service import UserService
from schemas.user import AdminUserOut, AdminUserListResponse, UserDeleteResponse
from core.security import get_current_admin   #  관리자 권한 의존성 가져오기

router = APIRouter(prefix="/admin", tags=["admin"])

# -----------------------------
# 전체 사용자 조회 (관리자 전용)
# -----------------------------
@router.get("/users", response_model=AdminUserListResponse)
async def get_all_users(
    current_admin: User = Depends(get_current_admin)  #  관리자 권한 검사
) -> AdminUserListResponse:
    users = await UserService.get_all_users()
    return AdminUserListResponse(
        users=[AdminUserOut.model_validate(u) for u in users],
        total=len(users),
    )

# -----------------------------
# 특정 사용자 조회 (관리자 전용)
# -----------------------------
@router.get("/users/{user_id}", response_model=AdminUserOut)
async def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),  #  의존성 추가
) -> AdminUserOut:
    if "@" in search:
        user = await UserService.get_user_by_email(search)  # 이메일 검색
    else:
        user = await UserService.get_user_by_username(search)  # 닉네임 검색

    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")

    return AdminUserOut.model_validate(user)

# -----------------------------
# 사용자 삭제 (관리자 전용)
# -----------------------------
@router.delete("/users/{user_id}", response_model=UserDeleteResponse)
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),  #  의존성 추가
) -> UserDeleteResponse:
    deleted = await UserService.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    # ✅ 명세서 기준: success 필드 반드시 반환
    return UserDeleteResponse(success=True)

# -----------------------------
# 사용자 활성/비활성 상태 변경 (관리자 전용)
# -----------------------------
@router.patch("/users/{user_id}/status", response_model=AdminUserOut)
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_admin: User = Depends(get_current_admin),  #  의존성 추가
) -> AdminUserOut:
    user = await UserService.update_user_status(user_id, is_active)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return AdminUserOut.model_validate(user)
