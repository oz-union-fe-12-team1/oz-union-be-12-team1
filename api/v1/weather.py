from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from services.weather_service import WeatherService
from models.user import User
from models.user_locations import UserLocation
from core.security import get_current_user

router = APIRouter(prefix="/weather", tags=["Weather"])

# 🌤 오늘의 날씨
@router.get("/", summary="현재 사용자 위치 기반 날씨 조회")
async def get_current_weather(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    #유저 로케이션에서 가져온 값으로 날씨 처리
    user_location = await UserLocation.get_or_none(user_id=current_user.id)
    if not user_location:
        raise HTTPException(status_code=404, detail="USER_LOCATION_NOT_FOUND")

    weather_data = await WeatherService.fetch_weather(
        lat=float(user_location.latitude),
        lon=float(user_location.longitude),
    )
    if not weather_data:
        raise HTTPException(status_code=400, detail="날씨 불러오기 실패")

    return {
        "success": True,
        "data": {
            "label": user_location.label,
            "latitude": user_location.latitude,
            "longitude": user_location.longitude,
            "weather": weather_data,
        },
    }


# 🌦 5일치 예보
@router.get("/forecast", summary="현재 사용자 위치 기반 5일치 예보 조회")
async def get_weather_forecast(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """DB의 user_locations에서 좌표를 불러와 예보 조회"""
    user_location = await UserLocation.get_or_none(user_id=current_user.id)
    if not user_location:
        raise HTTPException(status_code=404, detail="USER_LOCATION_NOT_FOUND")

    forecast_data = await WeatherService.fetch_forecast(
        lat=float(user_location.latitude),
        lon=float(user_location.longitude),
    )
    if not forecast_data:
        raise HTTPException(status_code=400, detail="날씨 예보 불러오기 실패")

    return {
        "success": True,
        "data": {
            "label": user_location.label,
            "latitude": user_location.latitude,
            "longitude": user_location.longitude,
            "forecast": forecast_data,
        },
    }
