from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from core.security import get_current_user
from services.user_location_service import UserLocationService
from schemas.user_locations import (
    UserLocationUpdateRequest,
    UserLocationUpdateResponse,
)

router = APIRouter(prefix="/locations", tags=["User Locations"])


# ✅ 내 위치 수정 (업데이트 전용)
@router.put("/me", response_model=UserLocationUpdateResponse)
async def update_my_location(
    update_data: UserLocationUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    """
    로그인한 사용자의 위치 정보 업데이트
    - 프론트에서 받은 위도/경도를 DB에 저장
    - 날씨 API 등에서 활용 가능
    """
    updated_location = await UserLocationService.update_location(
        location_id=current_user.id,  # user_id와 1:1 매핑이라면 이렇게 처리
        **update_data.dict(exclude_unset=True),
    )
    if not updated_location:
        raise HTTPException(status_code=404, detail="LOCATION_NOT_FOUND")

    return updated_location
