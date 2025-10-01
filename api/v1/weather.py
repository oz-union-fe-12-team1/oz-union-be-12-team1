from typing import Any
from fastapi import APIRouter, Query, HTTPException, Depends
from services.weather_service import WeatherService
from models.user import User
from models.user_locations import UserLocation
from core.security import get_current_user  # 현재 로그인 유저 불러오기

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("")
async def get_current_weather(
    lat: float | None = Query(None, description="위도 (테스트용, 선택)"),
    lon: float | None = Query(None, description="경도 (테스트용, 선택)"),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    현재 날씨 API
    - 프론트에서 lat/lon 주면 그 값 사용
    - 안 주면 user_location 테이블에서 조회
    """

    # DB 조회 (lat/lon 없을 때만)
    if lat is None or lon is None:
        user_loc = await UserLocation.get_or_none(user=current_user.id, is_default=True)
        if not user_loc:
            raise HTTPException(status_code=400, detail="위치 정보가 없습니다.")
        lat, lon = float(user_loc.latitude), float(user_loc.longitude)  # Decimal → float 변환

    # OpenWeather API 호출
    weather_data = await WeatherService.fetch_weather(lat, lon)
    if not weather_data:
        raise HTTPException(status_code=400, detail="날씨 불러오기 실패")

    return {"success": True, "data": weather_data}
