from fastapi import APIRouter, Depends, HTTPException
from decimal import Decimal
from models.user_locations import UserLocation
from models.user import User
from schemas.user_locations import UserLocationUpdateRequest, UserLocationUpdateResponse
from core.security import get_current_user

router = APIRouter(prefix="/user-locations", tags=["User Location"])


@router.patch("/", response_model=UserLocationUpdateResponse)
async def update_user_location(
    request: UserLocationUpdateRequest,
    current_user: User = Depends(get_current_user)
) -> UserLocationUpdateResponse:

    # 로그인한 사용자의 위치 정보를 업데이트하거나 없으면 새로 생성
    user_location = await UserLocation.get_or_none(user_id=current_user.id)

    # ✅ 없으면 새로 생성
    if not user_location:
        user_location = await UserLocation.create(
            user_id=current_user.id,
            latitude=Decimal(str(request.latitude)) if request.latitude is not None else Decimal("0"),
            longitude=Decimal(str(request.longitude)) if request.longitude is not None else Decimal("0"),
            label=request.label,
            is_default=request.is_default if request.is_default is not None else True,
        )

    # 있으면 업데이트
    else:
        if request.latitude is not None:
            user_location.latitude = Decimal(str(request.latitude))
        if request.longitude is not None:
            user_location.longitude = Decimal(str(request.longitude))
        if request.label is not None:
            user_location.label = request.label
        if request.is_default is not None:
            user_location.is_default = request.is_default

        await user_location.save()

    return UserLocationUpdateResponse.model_validate(user_location, from_attributes=True)