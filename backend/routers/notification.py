"""Notifications Router"""
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
async def list_notifications(unread_only: bool = Query(False), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        query = query.where(Notification.is_read == False)
    results = (await db.execute(query.order_by(Notification.created_at.desc()).limit(50))).scalars().all()
    unread = sum(1 for n in results if not n.is_read)
    return APIResponse(success=True, data={"notifications": [NotificationOut.model_validate(n) for n in results], "unread_count": unread})

@router.post("/{notif_id}/read", response_model=APIResponse)
async def mark_read(notif_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(update(Notification).where(Notification.id == notif_id, Notification.user_id == current_user.id).values(is_read=True))
    return APIResponse(success=True, message="Marked as read")

@router.post("/read-all", response_model=APIResponse)
async def mark_all_read(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(update(Notification).where(Notification.user_id == current_user.id, Notification.is_read == False).values(is_read=True))
    return APIResponse(success=True, message="All notifications marked as read")
