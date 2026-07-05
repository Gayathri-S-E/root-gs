"""
ROOTGS — AI Operating System for Smart Agriculture
FastAPI Backend Entry Point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger
import os

from core.config import settings
from core.database import engine, Base
from core.response import APIResponse

from routers import (
    auth,
    farm,
    crop,
    disease,
    weather,
    market,
    scheme,
    chat,
    analytics,
    notification,
    irrigation,
    admin,
)


# ─── Rate Limiter ────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ─── Lifespan ────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & Shutdown events"""
    logger.info("🌱 ROOTGS Backend starting up...")
    logger.info(f"   Environment : {settings.APP_ENV}")
    logger.info(f"   AI Features : {settings.ENABLE_AI_FEATURES}")
    logger.info(f"   Demo Mode   : {settings.AI_DEMO_MODE}")

    # Create tables if they do not exist
    try:
        logger.info("Initializing database tables...")
        import models  # Load models to register them on Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            from sqlalchemy import text
            await conn.execute(text("ALTER TABLE farmer_profiles ADD COLUMN IF NOT EXISTS gemini_api_key VARCHAR(255);"))
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")

    # Create media directory (skipped on read-only filesystems like Vercel)
    try:
        os.makedirs("media/disease", exist_ok=True)
        os.makedirs("media/farms", exist_ok=True)
        os.makedirs("media/profiles", exist_ok=True)
    except OSError:
        logger.warning("Media directories could not be created (read-only filesystem). Use S3 for file storage.")

    yield

    logger.info("🌿 ROOTGS Backend shutting down...")


# ─── Application ─────────────────────────────────────────────────────
app = FastAPI(
    title="ROOTGS API",
    description="""
## 🌾 ROOTGS — AI Operating System for Smart Agriculture

An AI-powered agriculture platform that helps farmers make scientific, data-driven decisions.

### Features
- 🤖 **AI Crop Doctor** — Disease detection via computer vision
- 🌤️ **Weather Intelligence** — 7-day forecasts with crop advisories
- 💬 **AI Chatbot** — Agriculture expert in your pocket
- 🌊 **Smart Irrigation** — Water optimization engine
- 📈 **Market Intelligence** — Real-time price analytics
- 🏛️ **Government Schemes** — Eligibility checker & guides
- 📊 **Farm Analytics** — Yield prediction & profit tracking

### Authentication
Use **Bearer Token** (JWT) in the `Authorization` header.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── Rate Limiting ───────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── Middleware ──────────────────────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static Files ────────────────────────────────────────────────────
try:
    app.mount("/media", StaticFiles(directory="media"), name="media")
except Exception:
    logger.warning("Media directory not found. Static file serving disabled. Use S3 for file storage.")

# ─── Routers ─────────────────────────────────────────────────────────
API_V1 = "/api/v1"

app.include_router(auth.router,         prefix=f"{API_V1}/auth",         tags=["Authentication"])
app.include_router(farm.router,         prefix=f"{API_V1}/farms",        tags=["Farm Management"])
app.include_router(crop.router,         prefix=f"{API_V1}/crops",        tags=["Crop Management"])
app.include_router(disease.router,      prefix=f"{API_V1}/disease",      tags=["Crop Doctor"])
app.include_router(weather.router,      prefix=f"{API_V1}/weather",      tags=["Weather Intelligence"])
app.include_router(market.router,       prefix=f"{API_V1}/market",       tags=["Market Intelligence"])
app.include_router(scheme.router,       prefix=f"{API_V1}/schemes",      tags=["Government Schemes"])
app.include_router(chat.router,         prefix=f"{API_V1}/chat",         tags=["AI Chatbot"])
app.include_router(analytics.router,    prefix=f"{API_V1}/analytics",    tags=["Farm Analytics"])
app.include_router(notification.router, prefix=f"{API_V1}/notifications",tags=["Notifications"])
app.include_router(irrigation.router,   prefix=f"{API_V1}/irrigation",   tags=["Smart Irrigation"])
app.include_router(admin.router,        prefix=f"{API_V1}/admin",        tags=["Admin"])


# ─── Root & Health ───────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return APIResponse(
        success=True,
        message="🌾 ROOTGS API is running",
        data={"version": "1.0.0", "docs": "/docs"},
    )


@app.get("/health", tags=["Health"])
async def health_check():
    return APIResponse(
        success=True,
        message="Healthy",
        data={"status": "ok", "service": "rootgs-backend"},
    )

# Trigger reload: 4
