"""Admin Router"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database import get_db
from core.response import APIResponse
from core.dependencies import require_admin
from models.user import User
from models.farm import Farm
from models.disease import DiseaseReport
from schemas.user import UserOut
router = APIRouter()

@router.get("/stats", response_model=APIResponse)
async def get_admin_stats(admin = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    """Platform-wide analytics for admins."""
    user_count = (await db.execute(select(func.count(User.id)))).scalar_one()
    farm_count = (await db.execute(select(func.count(Farm.id)))).scalar_one()
    disease_count = (await db.execute(select(func.count(DiseaseReport.id)))).scalar_one()
    return APIResponse(success=True, data={"total_users": user_count, "total_farms": farm_count, "total_disease_reports": disease_count, "platform": "ROOTGS v1.0"})

@router.get("/users", response_model=APIResponse)
async def list_users(admin = Depends(require_admin), db: AsyncSession = Depends(get_db), role: str = Query(None), page: int = Query(1)):
    query = select(User)
    if role:
        query = query.where(User.role == role)
    results = (await db.execute(query.limit(50).offset((page - 1) * 50))).scalars().all()
    return APIResponse(success=True, data=[UserOut.model_validate(u) for u in results])

@router.patch("/users/{user_id}/toggle-active", response_model=APIResponse)
async def toggle_user(user_id: int, admin = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    from fastapi import HTTPException
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    await db.flush()
    return APIResponse(success=True, message=f"User {'activated' if user.is_active else 'deactivated'}")
