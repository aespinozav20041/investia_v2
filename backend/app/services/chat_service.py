from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage
from app.models.trading import Trade


class ChatService:
    async def explain_trade_decision(
        self, db: AsyncSession, *, user_id: int, question: str, trade_id: int | None = None
    ) -> str:
        trade_context = None
        if trade_id:
            result = await db.execute(
                select(Trade).where(Trade.id == trade_id, Trade.user_id == user_id)
            )
            trade_context = result.scalars().first()

        base_answer = "This is a simulated explanation based on our paper-trading engine. "
        if trade_context:
            base_answer += (
                f"For trade {trade_context.id} on {trade_context.symbol}, the model observed momentum and order-book imbalance, "
                f"leading to a {trade_context.side} at ${trade_context.price}. "
            )
        else:
            base_answer += "The bot blends order book depth, sentiment, and quantitative signals to propose trades. "
        base_answer += (
            "Signals are generated in paper mode for safety. Connect a broker and upgrade your plan to enable higher fidelity models."
        )

        message = ChatMessage(user_id=user_id, question=question, answer=base_answer, created_at=datetime.utcnow())
        db.add(message)
        await db.commit()
        return base_answer


chat_service = ChatService()
