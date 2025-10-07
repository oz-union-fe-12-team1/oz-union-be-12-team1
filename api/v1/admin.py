from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any

from models.user import User
from repositories.user_repo import UserRepository
from services.user_service import UserService
from schemas.user import AdminUserOut, AdminUserListResponse, UserDeleteResponse
from core.security import get_current_user, get_current_admin   # 관리자 권한 의존성 가져오기

router = APIRouter(prefix="/admin", tags=["admin"])

# -----------------------------
# 전체 사용자 조회 (관리자 전용)
# -----------------------------
@router.get("/users", response_model=AdminUserListResponse)
async def get_all_users(
    current_user: User = Depends(get_current_user),
) -> AdminUserListResponse:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다.")

    # ORM 객체 그대로 가져오기
    users = await User.all().order_by("-created_at")

    # from_attributes=True 덕분에 자동 변환 가능
    return AdminUserListResponse(
        users=[AdminUserOut.model_validate(u, from_attributes=True) for u in users],
        total=len(users),
    )


# 특정 사용자 조회 (관리자 전용)

@router.get("/users/search", response_model=List[AdminUserOut])
async def search_users(
    search: str,
    current_user: User = Depends(get_current_user),
) ->AdminUserOut:
    """
    관리자 전용 — 유저 이름 또는 이메일 일부 검색
    ex) 'oh' → oh, ohna, ohnana 모두 반환
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다.")

    users = await UserRepository.search_users(search)
    if not users:
        raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")

    # ✅ dict 리스트를 AdminUserOut 모델로 변환
    return [AdminUserOut(**u) for u in users]
# -----------------------------
# 사용자 삭제 (관리자 전용)
# -----------------------------
@router.delete("/users/{user_id}", response_model=UserDeleteResponse)
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),  # 관리자 권한 검사
) -> UserDeleteResponse:
    deleted = await UserService.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    #  명세서 기준: success 필드 반드시 반환
    return UserDeleteResponse(success=True)

# -----------------------------
# 사용자 활성/비활성 상태 변경 (관리자 전용)
# -----------------------------
@router.patch("/users/{user_id}/status", response_model=AdminUserOut)
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_admin: User = Depends(get_current_admin),  # 관리자 권한 검사
) -> AdminUserOut:
    user = await UserService.update_user_status(user_id, is_active)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return AdminUserOut.model_validate(user)

# ---------------------------
# 전체 유저 최근 로그인 시간 조회 (관리자 전용)
# ---------------------------
@router.get("/users/last-login")
async def get_all_user_last_login(
    current_user: User = Depends(get_current_user)
) -> Dict[str, List[Dict]]:
    """
    🔒 관리자 전용 API
    전체 유저의 최근 로그인 시간을 조회합니다.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다.")

    users = await UserRepository.get_all_users_last_login()
    return {"users": users}