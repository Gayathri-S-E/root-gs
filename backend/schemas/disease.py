"""
Disease Detection Schemas
"""

from datetime import datetime
from typing import Optional, List
from schemas.base import OurBaseModel
from models.disease import DiseaseSeverity


class DiseaseDetectionResult(OurBaseModel):
    """Returned immediately after AI analyzes an image."""
    report_id: int
    crop_name: Optional[str] = None
    disease_name: Optional[str] = None
    disease_scientific_name: Optional[str] = None
    confidence_score: float
    severity: DiseaseSeverity
    affected_area_percent: Optional[float] = None

    # Explainable AI
    description: Optional[str] = None
    reason: Optional[str] = None
    evidence: Optional[str] = None
    risk_level: Optional[str] = None

    # Treatments
    chemical_treatment: Optional[list] = None
    organic_treatment: Optional[list] = None
    prevention_tips: Optional[list] = None
    medicine_dosage: Optional[str] = None
    estimated_loss_percent: Optional[float] = None
    alternative_diagnosis: Optional[list] = None

    # Meta
    image_url: str
    processing_time_ms: Optional[int] = None
    ai_model_used: Optional[str] = None


class DiseaseReportOut(OurBaseModel):
    id: int
    user_id: int
    farm_id: Optional[int] = None
    image_url: str
    crop_name: Optional[str] = None
    disease_name: Optional[str] = None
    confidence_score: float
    severity: DiseaseSeverity
    description: Optional[str] = None
    is_verified: bool
    created_at: datetime


class DiseaseReportUpdate(OurBaseModel):
    farmer_notes: Optional[str] = None
    farm_id: Optional[int] = None
    crop_cycle_id: Optional[int] = None


class TreatmentItem(OurBaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    notes: Optional[str] = None
