"""
Weather Service — Open-Meteo API integration (free, no key required)
"""

import httpx
import json
from typing import Optional
from datetime import datetime
import redis.asyncio as aioredis
from loguru import logger

from core.config import settings


WEATHER_CODE_MAP = {
    0: ("Clear Sky", "☀️"),
    1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Rime Fog", "🌫️"),
    51: ("Light Drizzle", "🌦️"),
    53: ("Moderate Drizzle", "🌦️"),
    55: ("Dense Drizzle", "🌧️"),
    61: ("Slight Rain", "🌧️"),
    63: ("Moderate Rain", "🌧️"),
    65: ("Heavy Rain", "🌧️"),
    71: ("Slight Snow", "❄️"),
    73: ("Moderate Snow", "❄️"),
    75: ("Heavy Snow", "❄️"),
    77: ("Snow Grains", "🌨️"),
    80: ("Slight Showers", "🌦️"),
    81: ("Moderate Showers", "🌦️"),
    82: ("Violent Showers", "⛈️"),
    85: ("Snow Showers", "🌨️"),
    86: ("Heavy Snow Showers", "🌨️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm w/ Hail", "⛈️"),
    99: ("Thunderstorm w/ Heavy Hail", "⛈️"),
}


CROP_ADVISORIES = {
    "heavy_rain": "⚠️ Heavy rain expected — delay fertilizer application. Check drainage in fields.",
    "high_wind": "⚠️ High winds — avoid pesticide spraying. Secure young plants and trellises.",
    "high_temp": "🌡️ Heat stress alert — irrigate in early morning or evening. Provide shade for nursery.",
    "low_humidity": "💧 Low humidity — increase irrigation frequency. Mulching recommended.",
    "frost_risk": "🥶 Frost risk — cover sensitive crops. Irrigate before frost to protect roots.",
    "ideal": "✅ Weather conditions are ideal for field operations today.",
    "fog": "🌫️ Foggy conditions — high fungal disease risk. Monitor crops closely.",
    "thunderstorm": "⛈️ Thunderstorm warning — stay indoors. Avoid fieldwork.",
}


class WeatherService:

    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def __init__(self):
        self._http = httpx.AsyncClient(timeout=15.0)

    async def get_weather(
        self,
        latitude: float,
        longitude: float,
        redis_client: Optional[aioredis.Redis] = None,
    ) -> dict:
        cache_key = f"weather:{latitude:.3f}:{longitude:.3f}"

        # Check Redis cache
        if redis_client:
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m", "relative_humidity_2m", "apparent_temperature",
                "is_day", "precipitation", "weather_code", "surface_pressure",
                "wind_speed_10m", "wind_direction_10m", "uv_index", "visibility",
            ],
            "daily": [
                "weather_code", "temperature_2m_max", "temperature_2m_min",
                "precipitation_sum", "wind_speed_10m_max", "sunrise", "sunset",
                "uv_index_max", "precipitation_probability_max",
            ],
            "timezone": "Asia/Kolkata",
            "forecast_days": 7,
        }

        try:
            resp = await self._http.get(self.BASE_URL, params=params)
            resp.raise_for_status()
            raw = resp.json()

            result = self._parse_weather(raw)

            # Cache for 30 minutes
            if redis_client:
                await redis_client.setex(cache_key, settings.WEATHER_CACHE_TTL, json.dumps(result))

            return result

        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return self._demo_weather(latitude, longitude)

    def _parse_weather(self, raw: dict) -> dict:
        current = raw.get("current", {})
        daily = raw.get("daily", {})

        wc = current.get("weather_code", 0)
        desc, icon = WEATHER_CODE_MAP.get(wc, ("Unknown", "🌡️"))
        temp = current.get("temperature_2m", 30)
        wind = current.get("wind_speed_10m", 0)
        humidity = current.get("relative_humidity_2m", 60)
        precip = current.get("precipitation", 0)

        # Generate alerts
        alerts = []
        advisory = CROP_ADVISORIES["ideal"]

        if precip > 20:
            alerts.append("Heavy rainfall warning")
            advisory = CROP_ADVISORIES["heavy_rain"]
        if wind > 40:
            alerts.append("High wind speed alert")
            advisory = CROP_ADVISORIES["high_wind"]
        if temp > 38:
            alerts.append("Heat stress alert for crops")
            advisory = CROP_ADVISORIES["high_temp"]
        if humidity < 30:
            advisory = CROP_ADVISORIES["low_humidity"]
        if wc in [45, 48]:
            advisory = CROP_ADVISORIES["fog"]
        if wc >= 95:
            alerts.append("Thunderstorm warning")
            advisory = CROP_ADVISORIES["thunderstorm"]

        # Build 7-day forecast
        forecast = []
        times = daily.get("time", [])
        for i in range(len(times)):
            day_wc = daily.get("weather_code", [0] * 7)[i] if i < len(daily.get("weather_code", [])) else 0
            day_desc, _ = WEATHER_CODE_MAP.get(day_wc, ("Clear", "☀️"))
            day_rain = daily.get("precipitation_sum", [0] * 7)[i] if i < len(daily.get("precipitation_sum", [])) else 0

            crop_adv = None
            if day_rain > 20:
                crop_adv = "Heavy rain — avoid spraying. Ensure drainage."
            elif day_wc >= 95:
                crop_adv = "Thunderstorm — stay indoors, secure equipment."

            forecast.append({
                "date": times[i],
                "temp_max": daily.get("temperature_2m_max", [30] * 7)[i] if i < len(daily.get("temperature_2m_max", [])) else 30,
                "temp_min": daily.get("temperature_2m_min", [20] * 7)[i] if i < len(daily.get("temperature_2m_min", [])) else 20,
                "precipitation_sum": day_rain,
                "wind_speed_max": daily.get("wind_speed_10m_max", [10] * 7)[i] if i < len(daily.get("wind_speed_10m_max", [])) else 10,
                "weather_code": day_wc,
                "description": day_desc,
                "sunrise": daily.get("sunrise", [""] * 7)[i] if i < len(daily.get("sunrise", [])) else "",
                "sunset": daily.get("sunset", [""] * 7)[i] if i < len(daily.get("sunset", [])) else "",
                "uv_index_max": daily.get("uv_index_max", [5] * 7)[i] if i < len(daily.get("uv_index_max", [])) else 5,
                "crop_advisory": crop_adv,
            })

        return {
            "latitude": raw.get("latitude", 0),
            "longitude": raw.get("longitude", 0),
            "location_name": None,
            "current": {
                "temperature": temp,
                "feels_like": current.get("apparent_temperature", temp),
                "humidity": humidity,
                "wind_speed": wind,
                "wind_direction": current.get("wind_direction_10m", 0),
                "pressure": current.get("surface_pressure", 1013),
                "visibility": current.get("visibility", 10000),
                "uv_index": current.get("uv_index", 5),
                "weather_code": wc,
                "description": desc,
                "icon": icon,
                "is_day": bool(current.get("is_day", 1)),
                "precipitation": precip,
            },
            "forecast": forecast,
            "alerts": alerts,
            "crop_advisory": advisory,
        }

    def _demo_weather(self, lat: float, lon: float) -> dict:
        """Fallback demo weather data."""
        return {
            "latitude": lat,
            "longitude": lon,
            "location_name": "Your Farm Location",
            "current": {
                "temperature": 32.5,
                "feels_like": 35.0,
                "humidity": 68.0,
                "wind_speed": 12.5,
                "wind_direction": 180.0,
                "pressure": 1008.0,
                "visibility": 8500.0,
                "uv_index": 7.5,
                "weather_code": 2,
                "description": "Partly Cloudy",
                "icon": "⛅",
                "is_day": True,
                "precipitation": 0.0,
            },
            "forecast": [
                {"date": "2024-06-30", "temp_max": 35, "temp_min": 24, "precipitation_sum": 0, "wind_speed_max": 15, "weather_code": 2, "description": "Partly Cloudy", "sunrise": "05:45", "sunset": "18:55", "uv_index_max": 8, "crop_advisory": None},
                {"date": "2024-07-01", "temp_max": 33, "temp_min": 23, "precipitation_sum": 12, "wind_speed_max": 20, "weather_code": 61, "description": "Slight Rain", "sunrise": "05:46", "sunset": "18:54", "uv_index_max": 3, "crop_advisory": "Rain expected — avoid fertilizer application"},
            ],
            "alerts": [],
            "crop_advisory": "✅ Weather conditions are suitable for field operations today.",
        }


weather_service = WeatherService()
