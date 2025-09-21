import os
from fastapi import APIRouter, Query, HTTPException
import httpx
from datetime import datetime

router = APIRouter()

# 환경변수에서 API 키 가져오기
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not OPENWEATHER_API_KEY:
    raise ValueError("OPENWEATHER_API_KEY environment variable is required")


@router.get("/weather")
async def get_current_weather(
    lat: float = Query(..., description="위도 (-90 ~ 90)", ge=-90, le=90),
    lon: float = Query(..., description="경도 (-180 ~ 180)", ge=-180, le=180),
):
    """현재 날씨 정보를 가져옵니다."""
    
    # OpenWeather API URL 구성
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=kr"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(url)
        
        # API 응답 상태 확인
        if res.status_code == 401:
            raise HTTPException(
                status_code=500, 
                detail="OpenWeather API 키가 유효하지 않습니다"
            )
        elif res.status_code == 404:
            raise HTTPException(
                status_code=404, 
                detail="해당 위치의 날씨 정보를 찾을 수 없습니다"
            )
        elif res.status_code != 200:
            data = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
            error_message = data.get("message", "OpenWeather API 오류가 발생했습니다")
            raise HTTPException(status_code=res.status_code, detail=error_message)
        
        data = res.json()
        
        # 필수 데이터 존재 확인
        if "main" not in data or "weather" not in data:
            raise HTTPException(
                status_code=500, 
                detail="날씨 API 응답 형식이 올바르지 않습니다"
            )
        
        # 안전한 데이터 추출
        weather_info = data.get("weather", [{}])[0] if data.get("weather") else {}
        main_info = data.get("main", {})
        wind_info = data.get("wind", {})
        
        return {
            "success": True,
            "data": {
                "city": data.get("name", "알 수 없는 지역"),
                "country": data.get("sys", {}).get("country"),
                "temperature": main_info.get("temp"),
                "feels_like": main_info.get("feels_like"),
                "temp_min": main_info.get("temp_min"),
                "temp_max": main_info.get("temp_max"),
                "description": weather_info.get("description", "정보 없음"),
                "main": weather_info.get("main"),
                "humidity": main_info.get("humidity"),
                "pressure": main_info.get("pressure"),
                "wind_speed": wind_info.get("speed"),
                "wind_direction": wind_info.get("deg"),
                "cloudiness": data.get("clouds", {}).get("all"),
                "visibility": data.get("visibility"),
                "sunrise": data.get("sys", {}).get("sunrise"),
                "sunset": data.get("sys", {}).get("sunset"),
                "coordinates": {
                    "lat": data.get("coord", {}).get("lat"),
                    "lon": data.get("coord", {}).get("lon")
                },
                "updated_at": datetime.now().isoformat(),
            },
        }
    
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=408, 
            detail="날씨 API 요청 시간이 초과되었습니다"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"날씨 API 요청 중 오류가 발생했습니다: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"응답 데이터 처리 중 오류가 발생했습니다: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"예상치 못한 오류가 발생했습니다: {str(e)}"
        )