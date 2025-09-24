from fastapi import APIRouter, Depends, HTTPException
from typing import List

from services.location_service import UserLocationService
from schemas.user_locations import (
    UserLocationResponse,
    UserLocationUpdateRequest,
    UserLocationUpdateResponse,
)
from core.security import get_current_user
from models.user import User

router = APIRouter(prefix="/locations", tags=["locations"])


# ✅ 내 위치 단일 조회
@router.get("/{location_id}", response_model=UserLocationResponse)
async def get_location(
    location_id: int, current_user: User = Depends(get_current_user)
):
    location = await UserLocationService.get_location_by_id(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="LOCATION_NOT_FOUND")
    return location


# ✅ 내 위치 전체 조회
@router.get("/", response_model=List[UserLocationResponse])
async def get_locations(current_user: User = Depends(get_current_user)):
    return await UserLocationService.get_locations_by_user(current_user.id)


# ✅ 내 위치 수정
@router.put("/{location_id}", response_model=UserLocationUpdateResponse)
async def update_location(
    location_id: int,
    request: UserLocationUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    updated_location = await UserLocationService.update_location(location_id, request)
    if not updated_location:
        raise HTTPException(status_code=404, detail="LOCATION_NOT_FOUND")
    return updated_location
