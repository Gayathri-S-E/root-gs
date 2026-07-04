"""
Weather Router — Current weather, 7-day forecast, crop advisories
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as aioredis

from core.database import get_db
from core.response import APIResponse
from core.dependencies import get_current_user, get_redis
from models.user import User
from services.weather.weather_service import weather_service

router = APIRouter()


@router.get("/current", response_model=APIResponse)
async def get_current_weather(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    current_user: User = Depends(get_current_user),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Get current weather + 7-day forecast with crop advisories."""
    data = await weather_service.get_weather(lat, lon, redis)
    return APIResponse(success=True, message="Weather loaded", data=data)


@router.get("/farm/{farm_id}", response_model=APIResponse)
async def get_farm_weather(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Get weather for a specific farm location."""
    from models.farm import Farm
    result = await db.execute(select(Farm).where(Farm.id == farm_id, Farm.owner_id == current_user.id))
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    if not farm.latitude or not farm.longitude:
        return APIResponse(success=False, message="Farm location not set. Please add GPS coordinates.")
    data = await weather_service.get_weather(farm.latitude, farm.longitude, redis)
    data["location_name"] = farm.name
    return APIResponse(success=True, data=data)
