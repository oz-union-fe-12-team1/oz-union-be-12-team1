from fastapi import APIRouter, HTTPException, Depends

from models.user import User
from services.user_service import UserService
from schemas.user import AdminUserOut, AdminUserListResponse, UserDeleteResponse
from core.security import get_current_admin   # ✅ 관리자 권한 의존성 가져오기

router = APIRouter(prefix="/admin", tags=["admin"])

# -----------------------------
# 전체 사용자 조회 (관리자 전용)
# -----------------------------
@router.get("/users", response_model=AdminUserListResponse)
async def get_all_users(current_admin: User = Depends(get_current_admin)) -> AdminUserListResponse:  # ✅ 관리자 권한 검사 의존성 추가
    users = await UserService.get_all_users()
    return AdminUserListResponse(users=[AdminUserOut.model_validate(u) for u in users], total=len(users))

# -----------------------------
# 특정 사용자 조회 (관리자 전용)
# -----------------------------
@router.get("/users/{user_id}", response_model=AdminUserOut)
async def get_user(user_id: int, current_admin: User = Depends(get_current_admin)) -> AdminUserOut:  # ✅ 의존성 추가
    user = await UserService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return AdminUserOut.model_validate(user)

# -----------------------------
# 사용자 삭제 (관리자 전용)
# -----------------------------
@router.delete("/users/{user_id}", response_model=UserDeleteResponse)
async def delete_user(user_id: int, current_admin: User = Depends(get_current_admin)) -> UserDeleteResponse:  # ✅ 의존성 추가
    deleted = await UserService.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return UserDeleteResponse()

# -----------------------------
# 사용자 활성/비활성 상태 변경 (관리자 전용)
# -----------------------------
@router.patch("/users/{user_id}/status", response_model=AdminUserOut)
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_admin: User = Depends(get_current_admin),  # ✅ 의존성 추가
) -> AdminUserOut:
    user = await UserService.update_user_status(user_id, is_active)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return AdminUserOut.model_validate(user)
