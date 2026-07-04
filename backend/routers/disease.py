"""
Disease Router — Image upload, AI detection, history
"""

import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.response import APIResponse, PaginatedResponse
from core.dependencies import get_current_user, get_pagination, PaginationParams
from models.disease import DiseaseReport
from models.user import User
from schemas.disease import DiseaseDetectionResult, DiseaseReportOut, DiseaseReportUpdate
from services.disease.disease_service import disease_service

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/detect", response_model=APIResponse)
async def detect_disease(
    image: UploadFile = File(..., description="Crop image for disease detection"),
    farm_id: Optional[int] = Form(None),
    crop_cycle_id: Optional[int] = Form(None),
    crop_hint: Optional[str] = Form(None, description="Hint about crop type"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a crop image and get AI-powered disease detection.

    Returns detailed disease analysis with:
    - Disease identification + confidence score
    - Severity assessment
    - Chemical and organic treatments
    - Prevention tips
    - Explainable AI fields (reason, evidence, risk)
    """
    # Validate file type
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )

    # Read and validate size
    image_bytes = await image.read()
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Image too large. Max 10MB.")

    # Run detection pipeline
    report = await disease_service.detect_disease(
        image_bytes=image_bytes,
        filename=image.filename or "upload.jpg",
        user=current_user,
        db=db,
        farm_id=farm_id,
        crop_cycle_id=crop_cycle_id,
        crop_hint=crop_hint,
    )

    # Parse JSON fields for response
    def safe_json(val):
        if val is None:
            return None
        try:
            return json.loads(val)
        except Exception:
            return val

    result = DiseaseDetectionResult(
        report_id=report.id,
        crop_name=report.crop_name,
        disease_name=report.disease_name,
        disease_scientific_name=report.disease_scientific_name,
        confidence_score=report.confidence_score,
        severity=report.severity,
        affected_area_percent=report.affected_area_percent,
        description=report.description,
        reason=report.reason,
        evidence=report.evidence,
        risk_level=report.risk_level,
        chemical_treatment=safe_json(report.chemical_treatment),
        organic_treatment=safe_json(report.organic_treatment),
        prevention_tips=safe_json(report.prevention_tips),
        medicine_dosage=report.medicine_dosage,
        estimated_loss_percent=report.estimated_loss_percent,
        alternative_diagnosis=safe_json(report.alternative_diagnosis),
        image_url=report.image_url,
        processing_time_ms=report.processing_time_ms,
        ai_model_used=report.ai_model_used,
    )

    return APIResponse(
        success=True,
        message=f"AI Analysis Complete — {report.disease_name or 'Analysis ready'}",
        data=result,
    )


@router.get("/history", response_model=APIResponse)
async def get_disease_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination),
    farm_id: Optional[int] = Query(None),
):
    """Get disease detection history for the current user."""
    query = select(DiseaseReport).where(DiseaseReport.user_id == current_user.id)
    if farm_id:
        query = query.where(DiseaseReport.farm_id == farm_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    query = query.offset(pagination.offset).limit(pagination.page_size).order_by(DiseaseReport.created_at.desc())
    reports = (await db.execute(query)).scalars().all()

    return APIResponse(
        success=True,
        message=f"{total} report(s) found",
        data=PaginatedResponse.create(
            data=[DiseaseReportOut.model_validate(r) for r in reports],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        ),
    )


@router.get("/{report_id}", response_model=APIResponse)
async def get_disease_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific disease report by ID."""
    result = await db.execute(
        select(DiseaseReport).where(
            DiseaseReport.id == report_id,
            DiseaseReport.user_id == current_user.id,
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    def safe_json(val):
        if val is None:
            return None
        try:
            return json.loads(val)
        except Exception:
            return val

    result_data = DiseaseDetectionResult(
        report_id=report.id,
        crop_name=report.crop_name,
        disease_name=report.disease_name,
        disease_scientific_name=report.disease_scientific_name,
        confidence_score=report.confidence_score,
        severity=report.severity,
        affected_area_percent=report.affected_area_percent,
        description=report.description,
        reason=report.reason,
        evidence=report.evidence,
        risk_level=report.risk_level,
        chemical_treatment=safe_json(report.chemical_treatment),
        organic_treatment=safe_json(report.organic_treatment),
        prevention_tips=safe_json(report.prevention_tips),
        medicine_dosage=report.medicine_dosage,
        estimated_loss_percent=report.estimated_loss_percent,
        alternative_diagnosis=safe_json(report.alternative_diagnosis),
        image_url=report.image_url,
        processing_time_ms=report.processing_time_ms,
        ai_model_used=report.ai_model_used,
    )
    return APIResponse(success=True, data=result_data)


@router.patch("/{report_id}", response_model=APIResponse)
async def update_disease_report(
    report_id: int,
    payload: DiseaseReportUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add farmer notes or link to farm/crop cycle."""
    result = await db.execute(
        select(DiseaseReport).where(DiseaseReport.id == report_id, DiseaseReport.user_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(report, k, v)

    await db.flush()
    return APIResponse(success=True, message="Report updated")
