from typing import List, Optional
from repositories.user_locations_repo import UserLocationsRepository
from schemas.user_locations import (
    UserLocationResponse,
    UserLocationUpdateRequest,
    UserLocationUpdateResponse,
)


class LocationService:
    """
    Service layer for user locations.
    - 비즈니스 로직 담당
    - Repository 호출 후 응답을 스키마로 변환
    """

    def __init__(self, repo: UserLocationsRepository):
        self.repo = repo

    # ✅ 단일 위치 조회
    async def get_location(self, location_id: int) -> Optional[UserLocationResponse]:
        location = await self.repo.get_location_by_id(location_id)
        if not location:
            return None
        return UserLocationResponse.model_validate(location)

    # ✅ 사용자 위치 목록 조회
    async def get_user_locations(self, user_id: int) -> List[UserLocationResponse]:
        locations = await self.repo.get_locations_by_user(user_id)
        return [UserLocationResponse.model_validate(loc) for loc in locations]

    # ✅ 위치 수정
    async def update_location(
        self, location_id: int, update_data: UserLocationUpdateRequest
    ) -> Optional[UserLocationUpdateResponse]:
        # 요청에서 실제 들어온 필드만 반영
        data = update_data.model_dump(exclude_unset=True)
        location = await self.repo.update_location(location_id, **data)
        if not location:
            return None
        return UserLocationUpdateResponse.model_validate(location)
