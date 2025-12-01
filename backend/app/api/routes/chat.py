from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    payload: ChatRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user=Depends(deps.get_current_active_user),
):
    answer = await chat_service.explain_trade_decision(
        db, user_id=current_user.id, question=payload.question, trade_id=payload.trade_id
    )
    return ChatResponse(answer=answer)
