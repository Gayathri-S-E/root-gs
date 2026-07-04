"""
Farm schemas
"""

from datetime import datetime
from typing import Optional, List
from schemas.base import OurBaseModel
from models.farm import SoilType, IrrigationType


class FarmCreate(OurBaseModel):
    name: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    total_area_acres: float
    soil_type: SoilType = SoilType.loamy
    irrigation_type: IrrigationType = IrrigationType.rainfed


class FarmUpdate(OurBaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    total_area_acres: Optional[float] = None
    soil_type: Optional[SoilType] = None
    irrigation_type: Optional[IrrigationType] = None
    cover_image: Optional[str] = None


class FieldCreate(OurBaseModel):
    name: str
    area_acres: float
    soil_type: SoilType = SoilType.loamy
    coordinates: Optional[str] = None
    current_crop: Optional[str] = None
    notes: Optional[str] = None


class FieldOut(OurBaseModel):
    id: int
    farm_id: int
    name: str
    area_acres: float
    soil_type: SoilType
    coordinates: Optional[str] = None
    current_crop: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime


class SoilReportCreate(OurBaseModel):
    field_id: Optional[int] = None
    ph: Optional[float] = None
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    organic_matter: Optional[float] = None
    moisture: Optional[float] = None
    texture: Optional[str] = None
    lab_name: Optional[str] = None
    sample_date: Optional[str] = None


class SoilReportOut(OurBaseModel):
    id: int
    farm_id: int
    ph: Optional[float] = None
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    organic_matter: Optional[float] = None
    moisture: Optional[float] = None
    ai_recommendation: Optional[str] = None
    suitable_crops: Optional[str] = None
    created_at: datetime


class FarmOut(OurBaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    total_area_acres: float
    soil_type: SoilType
    irrigation_type: IrrigationType
    health_score: float
    water_usage_score: float
    carbon_score: float
    cover_image: Optional[str] = None
    is_active: bool
    created_at: datetime
    fields: List[FieldOut] = []
