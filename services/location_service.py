from typing import List, Optional, Any
from repositories.user_locations_repo import UserLocationsRepository
from schemas.user_locations import (
    UserLocationResponse,
    UserLocationUpdateResponse,
)


class UserLocationService:
    """
    Service layer for managing user locations (조회 & 수정 전용).
    """

    # ✅ 단일 조회
    @staticmethod
    async def get_location_by_id(location_id: int) -> Optional[UserLocationResponse]:
        location = await UserLocationsRepository.get_location_by_id(location_id)
        if not location:
            return None
        return UserLocationResponse.model_validate(location, from_attributes=True)

    # ✅ 사용자별 전체 조회
    @staticmethod
    async def get_locations_by_user(user_id: int) -> List[UserLocationResponse]:
        locations = await UserLocationsRepository.get_locations_by_user(user_id)
        return [UserLocationResponse.model_validate(loc, from_attributes=True) for loc in locations]

    # ✅ 수정
    @staticmethod
    async def update_location(location_id: int, **kwargs: Any) -> Optional[UserLocationUpdateResponse]:
        updated = await UserLocationsRepository.update_location(location_id, **kwargs)
        if not updated:
            return None
        return UserLocationUpdateResponse.model_validate(updated, from_attributes=True)
