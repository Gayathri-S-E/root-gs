"""
Chat, Weather, Market, Scheme, Analytics, Notification, Task Schemas
"""

from datetime import datetime, date
from typing import Optional, List, Any
from schemas.base import OurBaseModel


# ─── Chat ─────────────────────────────────────────────────────────────
class ChatMessageCreate(OurBaseModel):
    content: str
    language: str = "en"
    is_voice: bool = False
    farm_id: Optional[int] = None
    crop_name: Optional[str] = None


class ChatMessageOut(OurBaseModel):
    id: int
    session_id: int
    role: str
    content: str
    language: str
    reasoning: Optional[str] = None
    confidence: Optional[float] = None
    is_voice: bool
    created_at: datetime


class ChatSessionOut(OurBaseModel):
    id: int
    user_id: int
    title: str
    language: str
    is_active: bool
    created_at: datetime
    messages: List[ChatMessageOut] = []


class ChatSessionCreate(OurBaseModel):
    title: str = "New Conversation"
    language: str = "en"


# ─── Weather ──────────────────────────────────────────────────────────
class WeatherCurrent(OurBaseModel):
    temperature: float
    feels_like: float
    humidity: float
    wind_speed: float
    wind_direction: float
    pressure: float
    visibility: float
    uv_index: float
    weather_code: int
    description: str
    icon: str
    is_day: bool
    precipitation: float


class WeatherForecastDay(OurBaseModel):
    date: str
    temp_max: float
    temp_min: float
    precipitation_sum: float
    wind_speed_max: float
    weather_code: int
    description: str
    sunrise: str
    sunset: str
    uv_index_max: float
    crop_advisory: Optional[str] = None


class WeatherResponse(OurBaseModel):
    latitude: float
    longitude: float
    location_name: Optional[str] = None
    current: WeatherCurrent
    forecast: List[WeatherForecastDay]
    alerts: List[str] = []
    crop_advisory: Optional[str] = None


# ─── Market ───────────────────────────────────────────────────────────
class MarketPriceOut(OurBaseModel):
    id: int
    crop_name: str
    market_name: str
    state: str
    district: Optional[str] = None
    price_date: date
    min_price: float
    max_price: float
    modal_price: float
    unit: str


class MarketTrend(OurBaseModel):
    crop_name: str
    market_name: str
    dates: List[str]
    prices: List[float]
    trend_direction: str  # up, down, stable
    trend_percentage: float
    best_sell_day: Optional[str] = None
    price_prediction_next_week: Optional[float] = None


class MarketCreate(OurBaseModel):
    crop_name: str
    market_name: str
    state: str
    district: Optional[str] = None
    price_date: date
    min_price: float
    max_price: float
    modal_price: float
    unit: str = "quintal"


# ─── Government Schemes ───────────────────────────────────────────────
class SchemeOut(OurBaseModel):
    id: int
    name: str
    scheme_code: Optional[str] = None
    authority: str
    state: Optional[str] = None
    category: str
    description: str
    benefits: Optional[str] = None
    eligibility: Optional[str] = None
    required_documents: Optional[str] = None
    application_url: Optional[str] = None
    deadline: Optional[date] = None
    max_benefit_amount: Optional[float] = None
    is_active: bool


class SchemeCreate(OurBaseModel):
    name: str
    authority: str
    state: Optional[str] = None
    category: str
    description: str
    benefits: Optional[str] = None
    eligibility: Optional[str] = None
    required_documents: Optional[str] = None
    application_url: Optional[str] = None
    deadline: Optional[date] = None
    max_benefit_amount: Optional[float] = None


class EligibilityCheck(OurBaseModel):
    scheme_id: int
    farmer_state: str
    land_acres: float
    crop_name: Optional[str] = None
    annual_income: Optional[float] = None


# ─── Notifications ────────────────────────────────────────────────────
class NotificationOut(OurBaseModel):
    id: int
    title: str
    body: str
    type: str
    is_read: bool
    action_url: Optional[str] = None
    created_at: datetime


# ─── Tasks ────────────────────────────────────────────────────────────
class TaskCreate(OurBaseModel):
    title: str
    description: Optional[str] = None
    farm_id: Optional[int] = None
    due_date: Optional[date] = None
    priority: str = "medium"
    category: Optional[str] = None


class TaskUpdate(OurBaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class TaskOut(OurBaseModel):
    id: int
    user_id: int
    farm_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: str
    priority: str
    category: Optional[str] = None
    is_ai_generated: bool
    created_at: datetime


# ─── Analytics ────────────────────────────────────────────────────────
class ExpenseCreate(OurBaseModel):
    farm_id: int
    crop_cycle_id: Optional[int] = None
    category: str
    description: str
    amount: float
    expense_date: date


class ExpenseOut(OurBaseModel):
    id: int
    farm_id: int
    category: str
    description: str
    amount: float
    expense_date: date
    created_at: datetime


class FarmAnalyticsSummary(OurBaseModel):
    farm_id: int
    farm_name: str
    total_expenses: float
    total_revenue: float
    net_profit: float
    profit_margin: float
    health_score: float
    water_usage_score: float
    carbon_score: float
    active_crop: Optional[str] = None
    yield_prediction: Optional[float] = None
    expense_breakdown: dict = {}


# ─── Irrigation ───────────────────────────────────────────────────────
class IrrigationRequest(OurBaseModel):
    farm_id: int
    crop_name: str
    area_acres: float
    soil_type: str
    current_stage: str  # sowing, vegetative, flowering, harvesting
    last_irrigation_days: int = 0
    rainfall_last_7_days_mm: float = 0


class IrrigationSchedule(OurBaseModel):
    recommended: bool
    water_required_liters: float
    next_irrigation_date: str
    frequency_days: int
    method: str
    reason: str
    confidence: float
    daily_schedule: List[dict] = []
    water_saving_tips: List[str] = []
    water_saving_score: float
