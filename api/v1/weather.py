from fastapi import APIRouter, Query, HTTPException
import httpx
from datetime import datetime
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

router = APIRouter()

# 환경 변수에서 API 키 가져오기
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


@router.get("/weather")
async def get_current_weather(
    lat: float = Query(..., description="위도"),
    lon: float = Query(..., description="경도"),
):
    if not OPENWEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenWeather API Key not found")

    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=kr"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(url)
    data = res.json()

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=data)

    return {
        "success": True,
        "data": {
            "city": data.get("name"),
            "temperature": data.get("main", {}).get("temp"),
            "description": data.get("weather", [{}])[0].get("description"),
            "humidity": data.get("main", {}).get("humidity"),
            "updated_at": datetime.now().isoformat(),
        },
    }
