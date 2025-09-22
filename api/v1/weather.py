from fastapi import APIRouter, Query, HTTPException
import httpx
from datetime import datetime
from core.config import settings  # config에서 불러오기

router = APIRouter()

# 환경변수에서 API 키 가져오기
OPENWEATHER_API_KEY = settings.OPENWEATHER_API_KEY
if not OPENWEATHER_API_KEY:
    raise ValueError("OPENWEATHER_API_KEY environment variable is required")


@router.get("/weather")
async def get_current_weather(
    lat: float = Query(..., description="위도 (-90 ~ 90)", ge=-90, le=90),
    lon: float = Query(..., description="경도 (-180 ~ 180)", ge=-180, le=180),
):
    """현재 날씨 정보를 가져옵니다."""

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=kr"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(url)

        if res.status_code == 401:
            raise HTTPException(status_code=500, detail="OpenWeather API 키가 유효하지 않습니다")
        elif res.status_code == 404:
            raise HTTPException(status_code=404, detail="해당 위치의 날씨 정보를 찾을 수 없습니다")
        elif res.status_code != 200:
            data = res.json() if "application/json" in res.headers.get("content-type", "") else {}
            error_message = data.get("message", "OpenWeather API 오류가 발생했습니다")
            raise HTTPException(status_code=res.status_code, detail=error_message)

        data = res.json()

        # 안전한 데이터 추출
        weather_info = (data.get("weather") or [{}])[0]
        main_info = data.get("main", {})
        wind_info = data.get("wind", {})
        sys_info = data.get("sys", {})
        coord_info = data.get("coord", {})

        # UNIX timestamp → ISO 포맷
        sunrise = sys_info.get("sunrise")
        sunset = sys_info.get("sunset")

        return {
            "success": True,
            "data": {
                "city": data.get("name", "알 수 없는 지역"),
                "country": sys_info.get("country"),
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
                "sunrise": datetime.fromtimestamp(sunrise).isoformat() if sunrise else None,
                "sunset": datetime.fromtimestamp(sunset).isoformat() if sunset else None,
                "coordinates": {
                    "lat": coord_info.get("lat"),
                    "lon": coord_info.get("lon"),
                },
            },
            "meta": {
                "requested_at": datetime.now().isoformat(),
                "requested_coords": {"lat": lat, "lon": lon},
            },
        }

    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="날씨 API 요청 시간이 초과되었습니다")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"날씨 API 요청 오류: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예상치 못한 오류가 발생했습니다: {str(e)}")
