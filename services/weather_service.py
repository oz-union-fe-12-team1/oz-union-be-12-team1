import httpx, os
from datetime import datetime

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

class WeatherService:
    @staticmethod
    async def fetch_weather(lat: float, lon: float) -> dict | None:
        """현재 날씨"""
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "kr",
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

    @staticmethod
    async def fetch_forecast(lat: float, lon: float) -> dict | None:
        """5일치 날씨 (3시간 단위 예보)"""
        url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "kr",
        }

        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(url, params=params)

        if res.status_code != 200:
            return None

        data = res.json()

        forecasts = []
        for item in data.get("list", []):
            forecasts.append({
                "time": item.get("dt_txt"),
                "temperature": item.get("main", {}).get("temp"),
                "description": item.get("weather", [{}])[0].get("description"),
                "humidity": item.get("main", {}).get("humidity"),
                "icon": item.get("weather", [{}])[0].get("icon"),
            })

        return {
            "city": data.get("city", {}).get("name"),
            "forecasts": forecasts,
            "updated_at": datetime.now().isoformat(),
        }