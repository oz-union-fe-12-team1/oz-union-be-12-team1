from fastapi import APIRouter, Depends, HTTPException
from typing import List

from repositories.user_locations_repo import UserLocationsRepository
from services.location_service import LocationService
from schemas.user_locations import (
    UserLocationResponse,
    UserLocationUpdateRequest,
    UserLocationUpdateResponse,
)

# 라우터 생성
router = APIRouter(prefix="/locations", tags=["User Locations"])

# Service 인스턴스
location_service = LocationService(UserLocationsRepository())


# ✅ 내 위치 단일 조회
@router.get("/{location_id}", response_model=UserLocationResponse)
async def get_location(location_id: int) -> UserLocationResponse:
    location = await location_service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


# ✅ 내 위치 전체 조회
@router.get("/", response_model=List[UserLocationResponse])
async def get_locations(user_id: int) -> List[UserLocationResponse]:  # 실제로는 Depends(get_current_user) 같은 인증 로직 들어감
    return await location_service.get_user_locations(user_id)


# ✅ 내 위치 수정
@router.put("/{location_id}", response_model=UserLocationUpdateResponse)
async def update_location(location_id: int, update_data: UserLocationUpdateRequest) -> UserLocationUpdateResponse:
    updated_location = await location_service.update_location(location_id, update_data)
    if not updated_location:
        raise HTTPException(status_code=404, detail="Location not found")
    return updated_location
