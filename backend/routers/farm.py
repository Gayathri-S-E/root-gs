"""
Farm Router — CRUD for farms, fields, soil reports
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.response import APIResponse, PaginatedResponse
from core.dependencies import get_current_user, get_pagination, PaginationParams
from models.farm import Farm, Field, SoilReport
from models.user import User
from schemas.farm import (
    FarmCreate, FarmUpdate, FarmOut,
    FieldCreate, FieldOut,
    SoilReportCreate, SoilReportOut,
)

router = APIRouter()


# ─── Farms ───────────────────────────────────────────────────────────
@router.post("", response_model=APIResponse)
async def create_farm(
    payload: FarmCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    farm = Farm(**payload.model_dump(), owner_id=current_user.id)
    db.add(farm)
    await db.flush()
    await db.refresh(farm)
    return APIResponse(success=True, message="Farm created successfully 🌾", data=FarmOut.model_validate(farm))


@router.get("", response_model=APIResponse)
async def list_farms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination),
    search: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
):
    query = select(Farm).where(Farm.owner_id == current_user.id, Farm.is_active == True)
    if search:
        query = query.where(Farm.name.ilike(f"%{search}%"))
    if state:
        query = query.where(Farm.state == state)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    query = query.offset(pagination.offset).limit(pagination.page_size).order_by(Farm.created_at.desc())
    farms = (await db.execute(query)).scalars().all()

    return APIResponse(
        success=True,
        message=f"{total} farm(s) found",
        data=PaginatedResponse.create(
            data=[FarmOut.model_validate(f) for f in farms],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        ),
    )


@router.get("/{farm_id}", response_model=APIResponse)
async def get_farm(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Farm).where(Farm.id == farm_id, Farm.owner_id == current_user.id)
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    # Load fields
    fields_result = await db.execute(select(Field).where(Field.farm_id == farm_id))
    farm.fields = list(fields_result.scalars().all())

    return APIResponse(success=True, message="Farm loaded", data=FarmOut.model_validate(farm))


@router.put("/{farm_id}", response_model=APIResponse)
async def update_farm(
    farm_id: int,
    payload: FarmUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Farm).where(Farm.id == farm_id, Farm.owner_id == current_user.id))
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(farm, k, v)

    await db.flush()
    return APIResponse(success=True, message="Farm updated", data=FarmOut.model_validate(farm))


@router.delete("/{farm_id}", response_model=APIResponse)
async def delete_farm(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Farm).where(Farm.id == farm_id, Farm.owner_id == current_user.id))
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    farm.is_active = False
    await db.flush()
    return APIResponse(success=True, message="Farm deactivated")


# ─── Fields ──────────────────────────────────────────────────────────
@router.post("/{farm_id}/fields", response_model=APIResponse)
async def create_field(
    farm_id: int,
    payload: FieldCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify farm ownership
    result = await db.execute(select(Farm).where(Farm.id == farm_id, Farm.owner_id == current_user.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Farm not found")

    field = Field(**payload.model_dump(), farm_id=farm_id)
    db.add(field)
    await db.flush()
    await db.refresh(field)
    return APIResponse(success=True, message="Field added", data=FieldOut.model_validate(field))


@router.get("/{farm_id}/fields", response_model=APIResponse)
async def list_fields(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Field).where(Field.farm_id == farm_id))
    fields = result.scalars().all()
    return APIResponse(success=True, data=[FieldOut.model_validate(f) for f in fields])


# ─── Soil Reports ────────────────────────────────────────────────────
@router.post("/{farm_id}/soil-reports", response_model=APIResponse)
async def create_soil_report(
    farm_id: int,
    payload: SoilReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from services.ai.gemini_client import gemini_client
    import json

    result = await db.execute(select(Farm).where(Farm.id == farm_id, Farm.owner_id == current_user.id))
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    # Get AI recommendation
    ai_rec = await gemini_client.get_crop_recommendation({
        "state": farm.state, "soil_type": farm.soil_type,
        "ph": payload.ph, "nitrogen": payload.nitrogen,
    })

    report = SoilReport(
        **payload.model_dump(),
        farm_id=farm_id,
        ai_recommendation=ai_rec.get("recommendation"),
        suitable_crops=json.dumps(ai_rec.get("alternatives", [])),
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)
    return APIResponse(success=True, message="Soil report added with AI analysis", data=SoilReportOut.model_validate(report))


@router.get("/{farm_id}/soil-reports", response_model=APIResponse)
async def list_soil_reports(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SoilReport).where(SoilReport.farm_id == farm_id).order_by(SoilReport.created_at.desc()))
    reports = result.scalars().all()
    return APIResponse(success=True, data=[SoilReportOut.model_validate(r) for r in reports])
