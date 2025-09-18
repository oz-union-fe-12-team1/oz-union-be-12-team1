from fastapi import APIRouter, Query, HTTPException
import httpx
from datetime import datetime

router = APIRouter()
OPENWEATHER_API_KEY = "db7f1228395d367de00a7e266352d8a9"


@router.get("/weather")
async def get_current_weather(
    lat: float = Query(..., description="위도"),
    lon: float = Query(..., description="경도"),
):
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
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "updated_at": datetime.now().isoformat(),
        },
    }
