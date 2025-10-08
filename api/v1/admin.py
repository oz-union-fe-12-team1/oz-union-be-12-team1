from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any

from models.user import User
from repositories.user_repo import UserRepository
from services.user_service import UserService
from schemas.user import AdminUserOut, AdminUserListResponse, UserDeleteResponse
from core.security import get_current_user, get_current_admin   # 관리자 권한 의존성 가져오기

router = APIRouter(prefix="/admin", tags=["admin"])


# 전체 사용자 조회 (관리자 전용)
@router.get("/users", response_model=AdminUserListResponse)
async def get_all_users(
    current_user: User = Depends(get_current_user),
) -> AdminUserListResponse:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다.")

    users = await User.all().order_by("-created_at")

    # is_google_user 계산해서 AdminUserOut으로 변환
    user_out_list = []
    for u in users:
        user_dict = u.__dict__.copy()
        user_dict["is_google_user"] = bool(getattr(u, "google_id", None))
        user_out_list.append(AdminUserOut.model_validate(user_dict))

    return AdminUserListResponse(users=user_out_list, total=len(users))



# 특정 사용자 검색 (관리자 전용)
@router.get("/users/search", response_model=List[AdminUserOut])
async def search_users(
    search: str,
    current_user: User = Depends(get_current_user),
) -> List[AdminUserOut]:
    """
    관리자 전용 — 유저 이름 또는 이메일 일부 검색
    ex) 'oh' → oh, ohna, ohnana 모두 반환
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다.")

    users = await UserRepository.search_users(search)
    if not users:
        raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")

    # ✅ dict 리스트 기반 변환 + 구글 로그인 여부 추가
    result = []
    for u in users:
        u["is_google_user"] = bool(u.get("google_id"))
        result.append(AdminUserOut(**u))
    return result



# 사용자 삭제 (관리자 전용)

@router.delete("/users/{user_id}", response_model=UserDeleteResponse)
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
) -> UserDeleteResponse:
    deleted = await UserService.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return UserDeleteResponse(success=True)


# 사용자 활성/비활성 상태 변경 (관리자 전용)
@router.patch("/users/{user_id}/status", response_model=AdminUserOut)
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_admin: User = Depends(get_current_admin),
) -> AdminUserOut:
    user = await UserService.update_user_status(user_id, is_active)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")

    # 구글 로그인 여부 계산 필드 추가
    user_dict = user.__dict__.copy()
    user_dict["is_google_user"] = bool(getattr(user, "google_id", None))
    return AdminUserOut.model_validate(user_dict)



# 전체 유저 최근 로그인 시간 조회 (관리자 전용)
@router.get("/users/last-login")
async def get_all_user_last_login(
    current_user: User = Depends(get_current_user),
) -> Dict[str, List[Dict]]:

    # 전체 유저의 최근 로그인 시간을 조회합니다.

    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다.")

    users = await UserRepository.get_all_users_last_login()
    # ✅ 구글 로그인 여부 추가
    for u in users:
        u["is_google_user"] = bool(u.get("google_id"))

    return {"users": users}
