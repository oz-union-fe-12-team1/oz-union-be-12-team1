from typing import Optional, List
from decimal import Decimal
from models.user_locations import UserLocation


class UserLocationsRepository:
    """
    Repository for managing user locations in DB.
    """

    @staticmethod
    async def get_locations_by_user(user_id: int) -> List[UserLocation]:
        return await UserLocation.filter(user_id=user_id).all()

    @staticmethod
    async def get_location_by_id(user_id: int, location_id: int) -> Optional[UserLocation]:
        return await UserLocation.filter(id=location_id, user_id=user_id).first()

    @staticmethod
    async def create_location(
        user_id: int,
        latitude: Decimal,
        longitude: Decimal,
        label: Optional[str],
        is_default: bool,
    ) -> UserLocation:
        return await UserLocation.create(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            label=label,
            is_default=is_default,
        )

    @staticmethod
    async def update_location(
        user_id: int,
        location_id: int,
        latitude: Decimal,
        longitude: Decimal,
        label: Optional[str],
        is_default: bool,
    ) -> Optional[UserLocation]:
        location = await UserLocation.filter(id=location_id, user_id=user_id).first()
        if not location:
            return None

        location.latitude = latitude
        location.longitude = longitude
        location.label = label
        location.is_default = is_default
        await location.save()

        return location

    @staticmethod
    async def delete_location(user_id: int, location_id: int) -> bool:
        deleted_count = await UserLocation.filter(id=location_id, user_id=user_id).delete()
        return deleted_count > 0
