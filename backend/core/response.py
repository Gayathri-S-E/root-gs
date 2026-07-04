"""
APIResponse — Unified response wrapper for all endpoints.
Every router must return APIResponse, never raw dicts.
"""

from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""
    success: bool = True
    message: str = "OK"
    data: Optional[T] = None
    errors: Optional[Any] = None

    model_config = {"arbitrary_types_allowed": True}


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""
    success: bool = True
    message: str = "OK"
    data: list[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0

    @classmethod
    def create(
        cls,
        data: list,
        total: int,
        page: int,
        page_size: int,
        message: str = "OK",
    ):
        import math
        return cls(
            success=True,
            message=message,
            data=data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if page_size > 0 else 0,
        )
