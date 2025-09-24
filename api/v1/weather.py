from fastapi import APIRouter, Query, HTTPException
import httpx, os
from datetime import datetime

router = APIRouter()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not OPENWEATHER_API_KEY:
    raise RuntimeError("❌ OPENWEATHER_API_KEY is not set")


@router.get("/weather")
async def get_current_weather(lat: float = Query(...), lon: float = Query(...)):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=kr"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(url)
    except httpx.RequestError:
        raise HTTPException(status_code=500, detail="날씨 요청 실패")

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail="날씨 불러오기 실패")

    data = res.json()
    return {
        "success": True,
        "data": {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "updated_at": datetime.now().isoformat(),
        },
    }
