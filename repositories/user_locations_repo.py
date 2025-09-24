from typing import List, Optional, Any
from tortoise.exceptions import DoesNotExist
from models.user_locations import UserLocation


class UserLocationsRepository:
    """
    Repository for managing user locations (조회 & 수정 전용).
    """

    # ✅ Read (단일 위치 조회)
    @staticmethod
    async def get_location_by_id(location_id: int) -> Optional[UserLocation]:
        try:
            return await UserLocation.get(id=location_id)
        except DoesNotExist:
            return None

    # ✅ Read (사용자별 위치 목록 조회)
    @staticmethod
    async def get_locations_by_user(user_id: int) -> List[UserLocation]:
        return await UserLocation.filter(user_id=user_id).order_by("-created_at")

    # ✅ Update (위치 정보 수정)
    @staticmethod
    async def update_location(location_id: int, **kwargs: Any) -> Optional[UserLocation]:
        """
        kwargs: 수정할 필드 전달 (latitude, longitude, name 등)
        """
        try:
            location = await UserLocation.get(id=location_id)
            for field, value in kwargs.items():
                setattr(location, field, value)
            await location.save()
            return location
        except DoesNotExist:
            return None
