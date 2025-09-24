from fastapi import APIRouter, Depends, HTTPException
from schemas.user import (
    AdminUserOut,
    AdminUserListResponse,
    UserDeleteResponse,
)
from services.user_service import UserService
from core.security import get_current_admin

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


# -----------------------------
# 전체 사용자 조회 (관리자 전용)
# -----------------------------
@router.get("/", response_model=AdminUserListResponse)
async def get_all_users(admin=Depends(get_current_admin)):
    """
    모든 사용자 목록 조회 (관리자 전용)
    """
    users = await UserService.get_all_users(admin=True)
    return users  # ✅ 이미 AdminUserListResponse 형태


# -----------------------------
# 단일 사용자 조회 (관리자 전용)
# -----------------------------
@router.get("/{user_id}", response_model=AdminUserOut)
async def get_user(user_id: int, admin=Depends(get_current_admin)):
    """
    특정 사용자 상세 조회 (관리자 전용)
    """
    user = await UserService.get_user_by_id(user_id, admin=True)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return user  # ✅ AdminUserOut 반환


# -----------------------------
# 사용자 활성/비활성 상태 변경
# -----------------------------
@router.patch("/{user_id}/status", response_model=AdminUserOut)
async def update_user_status(user_id: int, is_active: bool, admin=Depends(get_current_admin)):
    """
    사용자 활성/비활성 상태 변경 (관리자 전용)
    """
    user = await UserService.update_user_status(user_id, is_active)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return user  # ✅ AdminUserOut 반환


# -----------------------------
# 사용자 삭제 (관리자 전용)
# -----------------------------
@router.delete("/{user_id}", response_model=UserDeleteResponse)
async def delete_user(user_id: int, admin=Depends(get_current_admin)):
    """
    특정 사용자 삭제 (관리자 전용)
    """
    deleted = await UserService.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return deleted  # ✅ UserDeleteResponse 반환
