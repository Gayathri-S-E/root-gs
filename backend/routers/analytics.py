"""Analytics Router"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database import get_db
from core.response import APIResponse
from core.dependencies import get_current_user
from models.user import User
from models.farm import Farm
from models.analytics import Expense
from schemas.common import ExpenseCreate, ExpenseOut
router = APIRouter()

@router.get("/dashboard", response_model=APIResponse)
async def get_dashboard_summary(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get analytics summary for farmer dashboard."""
    farms_result = await db.execute(select(Farm).where(Farm.owner_id == current_user.id, Farm.is_active == True))
    farms = farms_result.scalars().all()
    total_expenses = 0
    summaries = []
    for farm in farms:
        exp = (await db.execute(select(func.sum(Expense.amount)).where(Expense.farm_id == farm.id))).scalar_one() or 0
        total_expenses += exp
        summaries.append({"farm_id": farm.id, "farm_name": farm.name, "health_score": farm.health_score, "water_usage_score": farm.water_usage_score, "carbon_score": farm.carbon_score, "total_expenses": exp})
    return APIResponse(success=True, data={"farm_count": len(farms), "total_expenses": total_expenses, "total_revenue": 0, "farms": summaries})

@router.post("/expenses", response_model=APIResponse)
async def add_expense(payload: ExpenseCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Record a farm expense."""
    r = await db.execute(select(Farm).where(Farm.id == payload.farm_id, Farm.owner_id == current_user.id))
    if not r.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Farm not found or access denied")
    expense = Expense(**payload.model_dump())
    db.add(expense)
    await db.flush()
    await db.refresh(expense)
    return APIResponse(success=True, message="Expense recorded", data=ExpenseOut.model_validate(expense))

@router.get("/expenses", response_model=APIResponse)
async def list_expenses(farm_id: Optional[int] = Query(None), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List expenses, optionally filtered by farm."""
    query = select(Expense).join(Farm).where(Farm.owner_id == current_user.id)
    if farm_id:
        query = query.where(Expense.farm_id == farm_id)
    results = (await db.execute(query.order_by(Expense.expense_date.desc()).limit(100))).scalars().all()
    return APIResponse(success=True, data=[ExpenseOut.model_validate(e) for e in results])
