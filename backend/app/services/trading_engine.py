import json
import random
from datetime import datetime
from uuid import uuid4
from typing import Any, Dict

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.trading import Trade
from app.models.user import PlanEnum, User
from app.services.data_ingestion_service import data_ingestion_service
from app.services.ml_model_service import ml_model_service


class TradingEngine:
    """Generates plan-aware paper trades and persists them."""

    def __init__(self) -> None:
        self.symbols = ["AAPL", "SPY", "BTC-USD", "ETH-USD", "NVDA", "MSFT"]
        try:
            self.redis: Redis | None = Redis.from_url(settings.REDIS_URL)
        except Exception:
            self.redis = None
        self._last_prices: dict[str, float] = {}

    def build_realtime_features(self, symbol: str) -> dict[str, float]:
        """Compose a feature dictionary aligned with model expectations."""
        order_book = data_ingestion_service.get_order_book_snapshot(symbol)
        sentiment = data_ingestion_service.get_sentiment_features(symbol)
        quant = data_ingestion_service.get_quant_features(symbol)
        last_price = self._last_prices.get(symbol, random.uniform(80, 220))
        price = max(1, last_price * (1 + random.uniform(-0.01, 0.01)))
        self._last_prices[symbol] = price

        log_return = float((price - last_price) / last_price) if last_price else 0.0
        return {
            "log_return": log_return,
            "volatility_10": random.uniform(0.005, 0.04),
            "volatility_20": random.uniform(0.005, 0.05),
            "volatility_50": random.uniform(0.005, 0.06),
            "ma_ratio": random.uniform(0.95, 1.05),
            "rsi_14": random.uniform(30, 70),
            "volume_zscore": random.uniform(-2, 2),
            "price_spread": random.uniform(0, 1),
            "sentiment_score": sentiment,
            "orderbook_depth": order_book,
            "quant_factor": quant,
            "price": price,
        }

    async def get_realtime_features(self, symbol: str) -> dict[str, float]:
        """Use Redis if available, otherwise synthesize."""
        if self.redis:
            try:
                cached = await self.redis.get(f"features:{symbol}")
                if cached:
                    data = json.loads(cached)
                    return {k: float(v) for k, v in data.items()}
            except Exception:
                pass
        return self.build_realtime_features(symbol)

    async def generate_trade_event(
        self, db: AsyncSession, *, user: User | None = None, symbol: str | None = None
    ) -> Dict[str, Any]:
        sym = symbol or random.choice(self.symbols)
        features = await self.get_realtime_features(sym)
        plan_value = user.plan.value if user and isinstance(user.plan, PlanEnum) else PlanEnum.free.value
        signal = await ml_model_service.predict_signal(plan_value, features, db)
        side = "buy" if signal == 1 else ("sell" if signal == -1 else "flat")
        quantity = round(random.uniform(0.1, 3.0), 2)
        price = round(features.get("price", random.uniform(50, 350)), 2)
        pnl = round(quantity * price * random.uniform(-0.002, 0.004), 2)
        explanation = (
            f"{plan_value.capitalize()} model generated {side} on {sym} "
            f"using sentiment={features['sentiment_score']:.2f} and order-book={features['orderbook_depth']:.2f}."
        )
        trade_data = {
            "user_id": user.id if user else 0,
            "symbol": sym,
            "side": side,
            "quantity": quantity,
            "price": price,
            "pnl": pnl,
            "explanation": explanation,
            "created_at": datetime.utcnow(),
        }
        return {"trade": trade_data, "features": features, "signal": signal, "event_id": str(uuid4())}

    async def record_trade(self, db: AsyncSession, trade_data: dict) -> Trade:
        trade = Trade(**trade_data)
        db.add(trade)
        await db.commit()
        await db.refresh(trade)
        return trade


trading_engine = TradingEngine()
