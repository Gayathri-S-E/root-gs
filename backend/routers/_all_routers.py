"""
Remaining Routers — Weather, Market, Scheme, Chat, Analytics, Irrigation, Notification, Crop, Admin
Each router follows the pattern: return APIResponse, never raw dicts.
"""

# ─── weather.py ───────────────────────────────────────────────────────
WEATHER_CONTENT = '''"""
Weather Router — Current weather, 7-day forecast, crop advisories
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.response import APIResponse
from core.dependencies import get_current_user, get_redis
from models.user import User
from services.weather.weather_service import weather_service
import redis.asyncio as aioredis

router = APIRouter()


@router.get("/current", response_model=APIResponse)
async def get_current_weather(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    current_user: User = Depends(get_current_user),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Get current weather + 7-day forecast with crop advisories."""
    data = await weather_service.get_weather(lat, lon, redis)
    return APIResponse(success=True, message="Weather loaded", data=data)


@router.get("/farm/{farm_id}", response_model=APIResponse)
async def get_farm_weather(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Get weather for a specific farm location."""
    from sqlalchemy import select
    from models.farm import Farm
    result = await db.execute(select(Farm).where(Farm.id == farm_id, Farm.owner_id == current_user.id))
    farm = result.scalar_one_or_none()
    if not farm:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Farm not found")
    if not farm.latitude or not farm.longitude:
        return APIResponse(success=False, message="Farm location not set. Please add GPS coordinates.")
    data = await weather_service.get_weather(farm.latitude, farm.longitude, redis)
    data["location_name"] = farm.name
    return APIResponse(success=True, data=data)
'''

# ─── chat.py ──────────────────────────────────────────────────────────
CHAT_CONTENT = '''"""
AI Chatbot Router — Multi-turn agriculture expert chat
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.response import APIResponse
from core.dependencies import get_current_user
from models.user import User
from models.analytics import ChatSession, ChatMessage
from schemas.common import ChatMessageCreate, ChatSessionCreate, ChatSessionOut, ChatMessageOut
from services.ai.gemini_client import gemini_client

router = APIRouter()


@router.post("/sessions", response_model=APIResponse)
async def create_session(
    payload: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = ChatSession(user_id=current_user.id, title=payload.title, language=payload.language)
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return APIResponse(success=True, message="Chat session started", data=ChatSessionOut.model_validate(session))


@router.get("/sessions", response_model=APIResponse)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession).where(ChatSession.user_id == current_user.id, ChatSession.is_active == True)
        .order_by(ChatSession.created_at.desc()).limit(20)
    )
    sessions = result.scalars().all()
    return APIResponse(success=True, data=[ChatSessionOut.model_validate(s) for s in sessions])


@router.post("/sessions/{session_id}/messages", response_model=APIResponse)
async def send_message(
    session_id: int,
    payload: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message to the AI agriculture chatbot."""
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Save user message
    user_msg = ChatMessage(
        session_id=session_id, role="user", content=payload.content,
        language=payload.language, is_voice=payload.is_voice,
    )
    db.add(user_msg)
    await db.flush()

    # Load conversation history (last 10 messages)
    hist_result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc()).limit(20)
    )
    history = [{"role": m.role, "content": m.content} for m in hist_result.scalars().all()]

    # AI response
    ai_resp = await gemini_client.chat_agriculture(history, payload.language)

    ai_msg = ChatMessage(
        session_id=session_id, role="assistant",
        content=ai_resp["content"], language=payload.language,
        reasoning=ai_resp.get("reasoning"),
        confidence=ai_resp.get("confidence"),
    )
    db.add(ai_msg)

    # Update session title if first message
    if len(history) <= 1:
        session.title = payload.content[:50] + ("..." if len(payload.content) > 50 else "")

    await db.flush()
    await db.refresh(ai_msg)
    return APIResponse(success=True, message="Response ready", data=ChatMessageOut.model_validate(ai_msg))


@router.get("/sessions/{session_id}/messages", response_model=APIResponse)
async def get_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    messages = result.scalars().all()
    return APIResponse(success=True, data=[ChatMessageOut.model_validate(m) for m in messages])
'''

# ─── market.py ────────────────────────────────────────────────────────
MARKET_CONTENT = '''"""
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
    query = select(MarketPrice).order_by(MarketPrice.price_date.desc())
    if state:
        query = query.where(MarketPrice.state == state)
    if crop_name:
        query = query.where(MarketPrice.crop_name.ilike(f"%{crop_name}%"))
    query = query.limit(50)
    results = (await db.execute(query)).scalars().all()
    return APIResponse(success=True, data=[MarketPriceOut.model_validate(r) for r in results])


@router.get("/prices/{crop_name}/trend", response_model=APIResponse)
async def get_price_trend(
    crop_name: str,
    state: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(MarketPrice).where(MarketPrice.crop_name.ilike(f"%{crop_name}%"))
    if state:
        query = query.where(MarketPrice.state == state)
    query = query.order_by(MarketPrice.price_date.asc()).limit(30)
    results = (await db.execute(query)).scalars().all()

    if not results:
        return APIResponse(success=True, data={"message": "No price data found", "dates": [], "prices": []})

    dates = [str(r.price_date) for r in results]
    prices = [r.modal_price for r in results]
    trend = "up" if len(prices) > 1 and prices[-1] > prices[0] else "down" if len(prices) > 1 and prices[-1] < prices[0] else "stable"
    pct = round((prices[-1] - prices[0]) / prices[0] * 100, 2) if prices[0] > 0 else 0

    return APIResponse(success=True, data={
        "crop_name": crop_name, "dates": dates, "prices": prices,
        "trend_direction": trend, "trend_percentage": pct,
        "best_sell_day": dates[-1] if trend == "up" else None,
    })


@router.post("/prices", response_model=APIResponse)
async def add_market_price(
    payload: MarketCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    price = MarketPrice(**payload.model_dump())
    db.add(price)
    await db.flush()
    await db.refresh(price)
    return APIResponse(success=True, message="Market price recorded", data=MarketPriceOut.model_validate(price))
'''

# ─── scheme.py ────────────────────────────────────────────────────────
SCHEME_CONTENT = '''"""
Government Schemes Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.response import APIResponse
from core.dependencies import get_current_user, require_admin
from models.user import User
from models.analytics import GovernmentScheme
from schemas.common import SchemeOut, SchemeCreate, EligibilityCheck

router = APIRouter()


@router.get("", response_model=APIResponse)
async def list_schemes(
    category: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
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
async def get_scheme(
    scheme_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(GovernmentScheme).where(GovernmentScheme.id == scheme_id))
    scheme = result.scalar_one_or_none()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return APIResponse(success=True, data=SchemeOut.model_validate(scheme))


@router.post("/check-eligibility", response_model=APIResponse)
async def check_eligibility(
    payload: EligibilityCheck,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(GovernmentScheme).where(GovernmentScheme.id == payload.scheme_id)
    )
    scheme = result.scalar_one_or_none()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Basic eligibility logic (can be enhanced with AI)
    eligible = True
    reasons = []
    if scheme.state and scheme.state != payload.farmer_state:
        eligible = False
        reasons.append(f"This scheme is only for {scheme.state} residents")

    return APIResponse(success=True, data={
        "scheme_id": payload.scheme_id,
        "scheme_name": scheme.name,
        "eligible": eligible,
        "reasons": reasons,
        "next_steps": "Visit your nearest Krishi Vigyan Kendra or Common Service Centre to apply."
        if eligible else "You may not qualify for this scheme.",
    })


@router.post("", response_model=APIResponse)
async def create_scheme(
    payload: SchemeCreate,
    admin_user = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    scheme = GovernmentScheme(**payload.model_dump())
    db.add(scheme)
    await db.flush()
    await db.refresh(scheme)
    return APIResponse(success=True, message="Scheme created", data=SchemeOut.model_validate(scheme))
'''

# ─── analytics.py ─────────────────────────────────────────────────────
ANALYTICS_CONTENT = '''"""
Analytics Router — Expenses, yield, profit dashboard
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.response import APIResponse
from core.dependencies import get_current_user
from models.user import User
from models.farm import Farm
from models.analytics import Expense, ExpenseCategory
from schemas.common import ExpenseCreate, ExpenseOut, FarmAnalyticsSummary

router = APIRouter()


@router.get("/dashboard", response_model=APIResponse)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """High-level analytics for the farmer dashboard."""
    farms_result = await db.execute(
        select(Farm).where(Farm.owner_id == current_user.id, Farm.is_active == True)
    )
    farms = farms_result.scalars().all()

    summaries = []
    total_revenue = 0
    total_expenses = 0

    for farm in farms:
        exp_result = await db.execute(
            select(func.sum(Expense.amount)).where(Expense.farm_id == farm.id)
        )
        expenses = exp_result.scalar_one() or 0
        total_expenses += expenses

        summaries.append({
            "farm_id": farm.id,
            "farm_name": farm.name,
            "health_score": farm.health_score,
            "water_usage_score": farm.water_usage_score,
            "carbon_score": farm.carbon_score,
            "total_expenses": expenses,
        })

    return APIResponse(success=True, data={
        "farm_count": len(farms),
        "total_expenses": total_expenses,
        "total_revenue": total_revenue,
        "farms": summaries,
    })


@router.post("/expenses", response_model=APIResponse)
async def add_expense(
    payload: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify farm ownership
    result = await db.execute(
        select(Farm).where(Farm.id == payload.farm_id, Farm.owner_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Farm not found or access denied")

    expense = Expense(**payload.model_dump())
    db.add(expense)
    await db.flush()
    await db.refresh(expense)
    return APIResponse(success=True, message="Expense recorded", data=ExpenseOut.model_validate(expense))


@router.get("/expenses", response_model=APIResponse)
async def list_expenses(
    farm_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Expense).join(Farm).where(Farm.owner_id == current_user.id)
    if farm_id:
        query = query.where(Expense.farm_id == farm_id)
    if category:
        query = query.where(Expense.category == category)
    results = (await db.execute(query.order_by(Expense.expense_date.desc()).limit(100))).scalars().all()
    return APIResponse(success=True, data=[ExpenseOut.model_validate(e) for e in results])
'''

# ─── irrigation.py ────────────────────────────────────────────────────
IRRIGATION_CONTENT = '''"""
Smart Irrigation Router
"""

from fastapi import APIRouter, Depends

from core.response import APIResponse
from core.dependencies import get_current_user
from models.user import User
from schemas.common import IrrigationRequest, IrrigationSchedule
from services.irrigation.irrigation_service import irrigation_service

router = APIRouter()


@router.post("/schedule", response_model=APIResponse)
async def get_irrigation_schedule(
    payload: IrrigationRequest,
    current_user: User = Depends(get_current_user),
):
    """Calculate smart irrigation schedule for a crop."""
    result = irrigation_service.calculate_schedule(
        crop_name=payload.crop_name,
        area_acres=payload.area_acres,
        soil_type=payload.soil_type,
        irrigation_type="drip",
        current_stage=payload.current_stage,
        last_irrigation_days=payload.last_irrigation_days,
        rainfall_last_7_days_mm=payload.rainfall_last_7_days_mm,
    )
    return APIResponse(success=True, message="Irrigation schedule calculated", data=result)
'''

# ─── notification.py ──────────────────────────────────────────────────
NOTIFICATION_CONTENT = '''"""
Notifications Router
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from core.database import get_db
from core.response import APIResponse
from core.dependencies import get_current_user
from models.user import User
from models.analytics import Notification
from schemas.common import NotificationOut

router = APIRouter()


@router.get("", response_model=APIResponse)
async def list_notifications(
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        query = query.where(Notification.is_read == False)
    query = query.order_by(Notification.created_at.desc()).limit(50)
    results = (await db.execute(query)).scalars().all()
    unread_count = sum(1 for n in results if not n.is_read)
    return APIResponse(success=True, data={"notifications": [NotificationOut.model_validate(n) for n in results], "unread_count": unread_count})


@router.post("/{notif_id}/read", response_model=APIResponse)
async def mark_read(
    notif_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(Notification).where(Notification.id == notif_id, Notification.user_id == current_user.id)
        .values(is_read=True)
    )
    return APIResponse(success=True, message="Marked as read")


@router.post("/read-all", response_model=APIResponse)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(Notification).where(Notification.user_id == current_user.id, Notification.is_read == False)
        .values(is_read=True)
    )
    return APIResponse(success=True, message="All notifications marked as read")
'''

# ─── crop.py ──────────────────────────────────────────────────────────
CROP_CONTENT = '''"""
Crop Management Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.response import APIResponse
from core.dependencies import get_current_user
from models.user import User
from models.crop import Crop, CropCycle
from models.farm import Farm

router = APIRouter()


@router.get("", response_model=APIResponse)
async def list_crops(
    search: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Crop)
    if search:
        query = query.where(Crop.name.ilike(f"%{search}%"))
    if season:
        query = query.where(Crop.season == season)
    if category:
        query = query.where(Crop.category == category)
    results = (await db.execute(query.limit(100))).scalars().all()
    return APIResponse(success=True, data=[{
        "id": c.id, "name": c.name, "local_name": c.local_name,
        "category": c.category, "season": c.season,
        "growth_days": c.growth_days, "image_url": c.image_url,
        "avg_yield_per_acre": c.avg_yield_per_acre,
    } for c in results])


@router.get("/{crop_id}", response_model=APIResponse)
async def get_crop(crop_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Crop).where(Crop.id == crop_id))
    crop = result.scalar_one_or_none()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return APIResponse(success=True, data=crop.__dict__)


@router.get("/recommend/for-farm/{farm_id}", response_model=APIResponse)
async def recommend_crops_for_farm(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from services.ai.gemini_client import gemini_client
    result = await db.execute(select(Farm).where(Farm.id == farm_id, Farm.owner_id == current_user.id))
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    context = {
        "state": farm.state, "district": farm.district,
        "soil_type": farm.soil_type, "area_acres": farm.total_area_acres,
        "irrigation_type": farm.irrigation_type,
    }
    recommendation = await gemini_client.get_crop_recommendation(context)
    return APIResponse(success=True, message="AI Crop Recommendation", data=recommendation)
'''

# ─── admin.py ─────────────────────────────────────────────────────────
ADMIN_CONTENT = '''"""
Admin Router — User management, system analytics
"""

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
async def get_admin_stats(
    admin = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user_count = (await db.execute(select(func.count(User.id)))).scalar_one()
    farm_count = (await db.execute(select(func.count(Farm.id)))).scalar_one()
    disease_count = (await db.execute(select(func.count(DiseaseReport.id)))).scalar_one()

    return APIResponse(success=True, data={
        "total_users": user_count,
        "total_farms": farm_count,
        "total_disease_reports": disease_count,
        "platform": "ROOTGS v1.0",
    })


@router.get("/users", response_model=APIResponse)
async def list_users(
    admin = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    role: str = Query(None),
    page: int = Query(1),
):
    query = select(User)
    if role:
        query = query.where(User.role == role)
    results = (await db.execute(query.limit(50).offset((page - 1) * 50))).scalars().all()
    return APIResponse(success=True, data=[UserOut.model_validate(u) for u in results])


@router.patch("/users/{user_id}/toggle-active", response_model=APIResponse)
async def toggle_user_active(
    user_id: int,
    admin = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    await db.flush()
    return APIResponse(success=True, message=f"User {'activated' if user.is_active else 'deactivated'}")
'''

import os

# Write all router files
routers = {
    "weather": WEATHER_CONTENT,
    "chat": CHAT_CONTENT,
    "market": MARKET_CONTENT,
    "scheme": SCHEME_CONTENT,
    "analytics": ANALYTICS_CONTENT,
    "irrigation": IRRIGATION_CONTENT,
    "notification": NOTIFICATION_CONTENT,
    "crop": CROP_CONTENT,
    "admin": ADMIN_CONTENT,
}

print("All router contents ready")
