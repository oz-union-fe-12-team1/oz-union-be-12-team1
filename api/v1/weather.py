from typing import Any
from fastapi import APIRouter, Query, HTTPException
from services.weather_service import WeatherService

router = APIRouter()

# 현재 날씨
@router.get("/weather")
async def get_current_weather(lat: float = Query(...), lon: float = Query(...)) -> dict[str, Any]:
    weather_data = await WeatherService.fetch_weather(lat, lon)
    if not weather_data:
        raise HTTPException(status_code=400, detail="날씨 불러오기 실패")
    return {"success": True, "data": weather_data}

# 5일치 예보
@router.get("/weather/forecast")
async def get_weather_forecast(lat: float = Query(...), lon: float = Query(...)) -> dict[str, Any]:
    forecast_data = await WeatherService.fetch_forecast(lat, lon)
    if not forecast_data:
        raise HTTPException(status_code=400, detail="날씨 예보 불러오기 실패")
    return {"success": True, "data": forecast_data}