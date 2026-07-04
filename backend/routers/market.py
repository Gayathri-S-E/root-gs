"""
Market Intelligence Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.response import APIResponse
from core.dependencies import get_current_user
from models.user import User
from models.analytics import MarketPrice
from schemas.common import MarketPriceOut, MarketCreate

router = APIRouter()


@router.get("/prices", response_model=APIResponse)
async def get_market_prices(
    state: Optional[str] = Query(None),
    crop_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get today's market prices, optionally filtered."""
    query = select(MarketPrice).order_by(MarketPrice.price_date.desc())
    if state:
        query = query.where(MarketPrice.state == state)
    if crop_name:
        query = query.where(MarketPrice.crop_name.ilike(f"%{crop_name}%"))
    results = (await db.execute(query.limit(50))).scalars().all()
    return APIResponse(success=True, data=[MarketPriceOut.model_validate(r) for r in results])


@router.get("/prices/{crop_name}/trend", response_model=APIResponse)
async def get_price_trend(
    crop_name: str,
    state: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get 30-day price trend for a crop with AI prediction."""
    query = select(MarketPrice).where(MarketPrice.crop_name.ilike(f"%{crop_name}%"))
    if state:
        query = query.where(MarketPrice.state == state)
    query = query.order_by(MarketPrice.price_date.asc()).limit(30)
    results = (await db.execute(query)).scalars().all()

    if not results:
        return APIResponse(success=True, data={"message": "No price data found", "dates": [], "prices": []})

    dates = [str(r.price_date) for r in results]
    prices = [r.modal_price for r in results]
    trend = "up" if prices[-1] > prices[0] else "down" if prices[-1] < prices[0] else "stable"
    pct = round((prices[-1] - prices[0]) / prices[0] * 100, 2) if prices[0] > 0 else 0

    return APIResponse(success=True, data={
        "crop_name": crop_name,
        "market_name": results[-1].market_name if results else "",
        "dates": dates,
        "prices": prices,
        "trend_direction": trend,
        "trend_percentage": pct,
        "best_sell_day": dates[-1] if trend == "up" else None,
        "price_prediction_next_week": round(prices[-1] * (1.02 if trend == "up" else 0.98), 2),
    })


@router.post("/prices", response_model=APIResponse)
async def add_market_price(
    payload: MarketCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a market price entry."""
    price = MarketPrice(**payload.model_dump())
    db.add(price)
    await db.flush()
    await db.refresh(price)
    return APIResponse(success=True, message="Market price recorded", data=MarketPriceOut.model_validate(price))
