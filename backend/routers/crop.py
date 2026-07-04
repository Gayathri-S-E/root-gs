"""Crop Management Router"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.response import APIResponse
from core.dependencies import get_current_user
from models.user import User
from models.crop import Crop
from models.farm import Farm
router = APIRouter()

@router.get("", response_model=APIResponse)
async def list_crops(search: Optional[str] = Query(None), season: Optional[str] = Query(None), category: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    """Browse the master crops database."""
    query = select(Crop)
    if search:
        query = query.where(Crop.name.ilike(f"%{search}%"))
    if season:
        query = query.where(Crop.season == season)
    if category:
        query = query.where(Crop.category == category)
    results = (await db.execute(query.limit(100))).scalars().all()
    return APIResponse(success=True, data=[{"id": c.id, "name": c.name, "local_name": c.local_name, "category": c.category, "season": c.season, "growth_days": c.growth_days, "image_url": c.image_url, "avg_yield_per_acre": c.avg_yield_per_acre, "water_requirement_mm": c.water_requirement_mm} for c in results])

@router.get("/{crop_id}", response_model=APIResponse)
async def get_crop(crop_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Crop).where(Crop.id == crop_id))
    crop = result.scalar_one_or_none()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return APIResponse(success=True, data={"id": crop.id, "name": crop.name, "local_name": crop.local_name, "scientific_name": crop.scientific_name, "category": crop.category, "season": crop.season, "growth_days": crop.growth_days, "water_requirement_mm": crop.water_requirement_mm, "ideal_temp_min": crop.ideal_temp_min, "ideal_temp_max": crop.ideal_temp_max, "description": crop.description, "common_diseases": crop.common_diseases})

@router.get("/recommend/for-farm/{farm_id}", response_model=APIResponse)
async def recommend_crops(farm_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get AI crop recommendation for a specific farm."""
    from services.ai.gemini_client import gemini_client
    result = await db.execute(select(Farm).where(Farm.id == farm_id, Farm.owner_id == current_user.id))
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    ctx = {"state": farm.state, "district": farm.district, "soil_type": str(farm.soil_type), "area_acres": farm.total_area_acres, "irrigation_type": str(farm.irrigation_type)}
    user_api_key = current_user.farmer_profile.gemini_api_key if current_user.farmer_profile else None
    rec = await gemini_client.get_crop_recommendation(ctx, api_key=user_api_key)
    return APIResponse(success=True, message="🌾 AI Crop Recommendation Ready", data=rec)
