import httpx
import os
from datetime import datetime
from typing import Optional

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


class WeatherService:
    @staticmethod
    async def fetch_weather(lat: float, lon: float) -> Optional[dict]:
        """현재 날씨 조회"""
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "ko",  # 권장값
        }

        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(url, params=params)

        if res.status_code != 200:
            return None

        data = res.json()
        return {
            "city": data.get("name"),
            "temperature": data.get("main", {}).get("temp"),
            "description": data.get("weather", [{}])[0].get("description"),
            "humidity": data.get("main", {}).get("humidity"),
            "icon": data.get("weather", [{}])[0].get("icon"),
            "updated_at": datetime.now().isoformat(),
        }
