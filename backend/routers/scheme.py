"""Government Schemes Router"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.response import APIResponse
from core.dependencies import get_current_user, require_admin
from models.user import User
from models.analytics import GovernmentScheme
from schemas.common import SchemeOut, SchemeCreate, EligibilityCheck
router = APIRouter()

@router.get("", response_model=APIResponse)
async def list_schemes(
    category: Optional[str] = Query(None), state: Optional[str] = Query(None),
    search: Optional[str] = Query(None), current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(GovernmentScheme).where(GovernmentScheme.is_active == True)
    if category:
        query = query.where(GovernmentScheme.category == category)
    if state:
        query = query.where((GovernmentScheme.state == state) | (GovernmentScheme.state == None))
    if search:
        query = query.where(GovernmentScheme.name.ilike(f"%{search}%"))
    results = (await db.execute(query.limit(50))).scalars().all()
    return APIResponse(success=True, data=[SchemeOut.model_validate(s) for s in results])

@router.get("/{scheme_id}", response_model=APIResponse)
async def get_scheme(scheme_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GovernmentScheme).where(GovernmentScheme.id == scheme_id))
    scheme = result.scalar_one_or_none()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return APIResponse(success=True, data=SchemeOut.model_validate(scheme))

@router.post("/check-eligibility", response_model=APIResponse)
async def check_eligibility(payload: EligibilityCheck, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GovernmentScheme).where(GovernmentScheme.id == payload.scheme_id))
    scheme = result.scalar_one_or_none()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    eligible = True
    reasons = []
    if scheme.state and scheme.state != payload.farmer_state:
        eligible = False
        reasons.append(f"This scheme is only for {scheme.state} residents")
    return APIResponse(success=True, data={
        "scheme_id": payload.scheme_id, "scheme_name": scheme.name,
        "eligible": eligible, "reasons": reasons,
        "next_steps": "Visit your nearest KVK or Common Service Centre to apply." if eligible else "You may not qualify.",
    })

@router.post("", response_model=APIResponse)
async def create_scheme(payload: SchemeCreate, admin = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    scheme = GovernmentScheme(**payload.model_dump())
    db.add(scheme)
    await db.flush()
    await db.refresh(scheme)
    return APIResponse(success=True, message="Scheme created", data=SchemeOut.model_validate(scheme))
