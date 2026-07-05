"""
Dependencies — FastAPI dependency injection
Provides: current_user, role guards, DB, Redis, pagination
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as aioredis
from functools import lru_cache

from core.database import get_db
from core.security import decode_token
from core.config import settings

# Import lazily to avoid circular imports
from jose import JWTError


# ─── Security Scheme ─────────────────────────────────────────────────
bearer_scheme = HTTPBearer(auto_error=False)


# ─── Redis Client ────────────────────────────────────────────────────
_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> Optional[aioredis.Redis]:
    """Returns Redis client, or None if Redis is unavailable (graceful degradation)."""
    global _redis_client
    if _redis_client is None:
        try:
            client = aioredis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True,
                socket_connect_timeout=2,
            )
            await client.ping()
            _redis_client = client
        except Exception:
            return None
    return _redis_client


# ─── Current User ────────────────────────────────────────────────────
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Validate JWT and return the current user model."""
    from models.user import User  # lazy import

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exception

    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated"
        )

    return user


async def get_current_active_user(current_user=Depends(get_current_user)):
    return current_user


# ─── Role Guards ─────────────────────────────────────────────────────
def require_role(*roles: str):
    """Factory: returns a dependency that enforces role membership."""

    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(roles)}",
            )
        return current_user

    return role_checker


require_admin = require_role("admin")
require_farmer = require_role("farmer", "admin")
require_officer = require_role("agriculture_officer", "agronomist", "admin")
require_researcher = require_role("researcher", "admin")


# ─── Optional Auth ───────────────────────────────────────────────────
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Returns user if authenticated, else None. For public endpoints."""
    if not credentials:
        return None
    try:
        from models.user import User

        payload = decode_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            return None
        result = await db.execute(select(User).where(User.id == int(user_id)))
        return result.scalar_one_or_none()
    except Exception:
        return None


# ─── Pagination ──────────────────────────────────────────────────────
class PaginationParams:
    def __init__(
        self,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ):
        self.page = max(1, page)
        self.page_size = min(page_size, settings.MAX_PAGE_SIZE)
        self.offset = (self.page - 1) * self.page_size


def get_pagination(
    page: int = 1,
    page_size: int = settings.DEFAULT_PAGE_SIZE,
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)
