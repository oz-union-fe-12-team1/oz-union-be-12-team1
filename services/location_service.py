from typing import Optional, List
from repositories.user_locations_repo import UserLocationsRepository
from schemas.user_locations import LocationUpdateRequest, LocationResponse
from models.user_locations import UserLocation


class LocationService:
    """
    Service layer for managing User Locations.
    """

    @staticmethod
    async def update_location(
        user_id: int, location_id: int, data: LocationUpdateRequest
    ) -> Optional[LocationResponse]:
        """
        사용자 위치 수정
        """
        updated: Optional[UserLocation] = await UserLocationsRepository.update_location(
            user_id=user_id,
            location_id=location_id,
            latitude=data.latitude,
            longitude=data.longitude,
            label=data.label,
            is_default=data.is_default,
        )
        if not updated:
            return None
        return LocationResponse.model_validate(updated, from_attributes=True)
