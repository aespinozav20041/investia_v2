from datetime import datetime

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
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

        base_prompt = [
            {
                "role": "system",
                "content": (
                    "You are Investia's trading explainer. Provide concise, transparent reasoning. "
                    "Do not promise profits; clarify that signals are simulated unless live trading is enabled."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ]
        if trade_context:
            base_prompt.append(
                {
                    "role": "user",
                    "content": (
                        f"Context: trade_id={trade_context.id}, symbol={trade_context.symbol}, "
                        f"side={trade_context.side}, price={trade_context.price}, pnl={trade_context.pnl}, "
                        f"created_at={trade_context.created_at}."
                    ),
                }
            )
        openai_answer = None
        if settings.OPENAI_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=20) as client:
                    resp = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": settings.MODEL_NAME,
                            "messages": base_prompt,
                            "max_tokens": 220,
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    openai_answer = data["choices"][0]["message"]["content"].strip()
            except Exception:
                openai_answer = None

        base_answer = openai_answer or self._fallback_answer(trade_context)

        message = ChatMessage(user_id=user_id, question=question, answer=base_answer, created_at=datetime.utcnow())
        db.add(message)
        await db.commit()
        return base_answer

    @staticmethod
    def _fallback_answer(trade_context: Trade | None) -> str:
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
        return base_answer


chat_service = ChatService()
