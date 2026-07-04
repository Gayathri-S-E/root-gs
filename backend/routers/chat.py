"""
AI Chatbot Router — Multi-turn agriculture expert chat
"""

from fastapi import APIRouter, Depends, HTTPException
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
    """Start a new AI chat session."""
    session = ChatSession(user_id=current_user.id, title=payload.title, language=payload.language)
    db.add(session)
    await db.flush()
    await db.refresh(session)
    session.messages = []
    return APIResponse(success=True, message="Chat session started 🤖", data=ChatSessionOut.model_validate(session))


@router.get("/sessions", response_model=APIResponse)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id, ChatSession.is_active == True)
        .order_by(ChatSession.created_at.desc())
        .limit(20)
    )
    sessions = result.scalars().all()
    for s in sessions:
        s.messages = []
    return APIResponse(success=True, data=[ChatSessionOut.model_validate(s) for s in sessions])


@router.post("/sessions/{session_id}/messages", response_model=APIResponse)
async def send_message(
    session_id: int,
    payload: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message to the AI agriculture chatbot and get expert response."""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id, ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Save user message
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=payload.content,
        language=payload.language,
        is_voice=payload.is_voice,
    )
    db.add(user_msg)
    await db.flush()

    # Load conversation history (last 20 messages for context)
    hist_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(20)
    )
    history = [{"role": m.role, "content": m.content} for m in hist_result.scalars().all()]

    # Add farm/crop context to the message if provided
    context_prefix = ""
    if payload.farm_id:
        context_prefix = f"[Context: Farm ID {payload.farm_id}"
        if payload.crop_name:
            context_prefix += f", Growing: {payload.crop_name}"
        context_prefix += "]\n"

    history[-1]["content"] = context_prefix + history[-1]["content"]

    # Get AI response
    user_api_key = current_user.farmer_profile.gemini_api_key if current_user.farmer_profile else None
    ai_resp = await gemini_client.chat_agriculture(history, payload.language, api_key=user_api_key)

    # Save AI response
    ai_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=ai_resp["content"],
        language=payload.language,
        reasoning=ai_resp.get("reasoning"),
        confidence=ai_resp.get("confidence"),
    )
    db.add(ai_msg)

    # Auto-title session from first message
    if len(history) <= 1:
        session.title = payload.content[:60] + ("..." if len(payload.content) > 60 else "")

    await db.flush()
    await db.refresh(ai_msg)
    return APIResponse(success=True, message="AI response ready", data=ChatMessageOut.model_validate(ai_msg))


@router.get("/sessions/{session_id}/messages", response_model=APIResponse)
async def get_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all messages in a chat session."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    messages = result.scalars().all()
    return APIResponse(success=True, data=[ChatMessageOut.model_validate(m) for m in messages])


@router.delete("/sessions/{session_id}", response_model=APIResponse)
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.is_active = False
    await db.flush()
    return APIResponse(success=True, message="Chat session deleted")
