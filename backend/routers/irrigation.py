"""Smart Irrigation Router"""
from fastapi import APIRouter, Depends
from core.response import APIResponse
from core.dependencies import get_current_user
from models.user import User
from schemas.common import IrrigationRequest
from services.irrigation.irrigation_service import irrigation_service
router = APIRouter()

@router.post("/schedule", response_model=APIResponse)
async def get_irrigation_schedule(payload: IrrigationRequest, current_user: User = Depends(get_current_user)):
    """Calculate a smart irrigation schedule based on crop, soil, and weather data."""
    result = irrigation_service.calculate_schedule(
        crop_name=payload.crop_name, area_acres=payload.area_acres,
        soil_type=payload.soil_type, irrigation_type="drip",
        current_stage=payload.current_stage, last_irrigation_days=payload.last_irrigation_days,
        rainfall_last_7_days_mm=payload.rainfall_last_7_days_mm,
    )
    return APIResponse(success=True, message="Irrigation schedule calculated 💧", data=result)
