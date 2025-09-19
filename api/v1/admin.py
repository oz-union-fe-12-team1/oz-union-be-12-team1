from fastapi import APIRouter, HTTPException
from services.user_service import UserService
from schemas.user import AdminUserOut, AdminUserListResponse, UserDeleteResponse

router = APIRouter(prefix="/admin", tags=["admin"])

# -----------------------------
# 전체 사용자 조회 (관리자 전용)
# -----------------------------
@router.get("/users", response_model=AdminUserListResponse)
async def get_all_users():
    users = await UserService.get_all_users()
    return {"users": [AdminUserOut.from_orm(u) for u in users], "total": len(users)}

# -----------------------------
# 특정 사용자 조회 (관리자 전용)
# -----------------------------
@router.get("/users/{user_id}", response_model=AdminUserOut)
async def get_user(user_id: int):
    user = await UserService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return AdminUserOut.from_orm(user)

# -----------------------------
# 사용자 삭제
# -----------------------------
@router.delete("/users/{user_id}", response_model=UserDeleteResponse)
async def delete_user(user_id: int):
    deleted = await UserService.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return {"message": "User deleted successfully"}

# -----------------------------
# 사용자 활성/비활성 상태 변경
# -----------------------------
@router.patch("/users/{user_id}/status", response_model=AdminUserOut)
async def update_user_status(user_id: int, is_active: bool):
    user = await UserService.update_user_status(user_id, is_active)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return AdminUserOut.from_orm(user)

# -----------------------------
# 관리자 권한 부여/회수
# -----------------------------
@router.patch("/users/{user_id}/superuser", response_model=AdminUserOut)
async def set_superuser(user_id: int, is_superuser: bool):
    user = await UserService.set_superuser(user_id, is_superuser)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return AdminUserOut.from_orm(user)
