import httpx, os
from datetime import datetime

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

class WeatherService:
    @staticmethod
    async def fetch_weather(lat: float, lon: float) -> dict | None:
        """현재 날씨 + 최고/최저/강수량/미세먼지"""
        base_url = "http://api.openweathermap.org/data/2.5"
        weather_url = f"{base_url}/weather"
        air_url = f"{base_url}/air_pollution"

        async with httpx.AsyncClient(timeout=10) as client:
            res_weather = await client.get(weather_url, params={
                "lat": lat,
                "lon": lon,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "lang": "kr",
            })

            if res_weather.status_code != 200:
                return None

            weather = res_weather.json()

            res_air = await client.get(air_url, params={
                "lat": lat,
                "lon": lon,
                "appid": OPENWEATHER_API_KEY,
            })
            air_data = None
            if res_air.status_code == 200:
                components = res_air.json().get("list", [{}])[0].get("components", {})
                air_data = {
                    "pm2_5": components.get("pm2_5"),
                    "pm10": components.get("pm10"),
                }

        return {
            "city": weather.get("name"),
            "temperature": weather.get("main", {}).get("temp"),
            "temp_max": weather.get("main", {}).get("temp_max"),
            "temp_min": weather.get("main", {}).get("temp_min"),
            "description": weather.get("weather", [{}])[0].get("description"),
            "humidity": weather.get("main", {}).get("humidity"),
            "rain_1h": weather.get("rain", {}).get("1h", 0),
            "snow_1h": weather.get("snow", {}).get("1h", 0),
            "pm2_5": air_data.get("pm2_5") if air_data else None,
            "pm10": air_data.get("pm10") if air_data else None,
            "icon": weather.get("weather", [{}])[0].get("icon"),
            "updated_at": datetime.now().isoformat(),
        }

    #  5일치 예보
    @staticmethod
    async def fetch_forecast(lat: float, lon: float) -> dict | None:
        """5일치 (3시간 간격) 예보 + 강수량/적설량 포함"""
        base_url = "http://api.openweathermap.org/data/2.5"
        forecast_url = f"{base_url}/forecast"
        air_url = f"{base_url}/air_pollution"

        async with httpx.AsyncClient(timeout=10) as client:
            res_forecast = await client.get(forecast_url, params={
                "lat": lat,
                "lon": lon,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "lang": "kr",
            })

            if res_forecast.status_code != 200:
                return None

            data = res_forecast.json()

            # 🌫 미세먼지 (현재 수치만 함께 포함)
            res_air = await client.get(air_url, params={
                "lat": lat,
                "lon": lon,
                "appid": OPENWEATHER_API_KEY,
            })
            air_data = None
            if res_air.status_code == 200:
                components = res_air.json().get("list", [{}])[0].get("components", {})
                air_data = {
                    "pm2_5": components.get("pm2_5"),
                    "pm10": components.get("pm10"),
                }

        forecasts = []
        for item in data.get("list", []):
            forecasts.append({
                "time": item.get("dt_txt"),
                "temperature": item.get("main", {}).get("temp"),
                "temp_max": item.get("main", {}).get("temp_max"),
                "temp_min": item.get("main", {}).get("temp_min"),
                "description": item.get("weather", [{}])[0].get("description"),
                "humidity": item.get("main", {}).get("humidity"),
                "rain_3h": item.get("rain", {}).get("3h", 0),
                "snow_3h": item.get("snow", {}).get("3h", 0),
                "icon": item.get("weather", [{}])[0].get("icon"),
            })

        return {
            "city": data.get("city", {}).get("name"),
            "pm2_5": air_data.get("pm2_5") if air_data else None,
            "pm10": air_data.get("pm10") if air_data else None,
            "forecasts": forecasts,
            "updated_at": datetime.now().isoformat(),
        }
