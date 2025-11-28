import asyncio
import logging
import math
import random
from datetime import datetime, timezone
from numbers import Number
from typing import Any

from sqlalchemy import select

from ..core.config import get_settings
from ..core.db import AsyncSessionLocal
from ..domain.plans.models import Plan
from ..domain.trading.models import Signal, Trade  # Trade kept for future paper trades
from ..domain.users.models import User
from ..services.model_service import ModelTier, predict_for_tier
from ..services.plan_service import PlanLimitExceeded, enforce_plan_limits_for_signal

logger = logging.getLogger(__name__)
settings = get_settings()

# Use configured interval when available, otherwise default to 60 seconds.
TRADING_LOOP_INTERVAL_SECONDS: int = getattr(settings, "TRADING_LOOP_INTERVAL_SECONDS", 60)
TEST_SYMBOL = "SPY"

# In-memory fake price state for development.
_price_state: dict[str, float] = {}


def plan_to_tier(plan_code: str | None) -> ModelTier:
    """Map plan code to ModelTier; default to FREEMIUM on unknown codes."""

    if not plan_code:
        logger.warning("Missing plan code; defaulting to FREEMIUM tier")
        return ModelTier.FREEMIUM

    code_upper = plan_code.upper()
    if code_upper == "FREEMIUM":
        return ModelTier.FREEMIUM
    if code_upper == "PLUS":
        return ModelTier.PLUS
    if code_upper == "ENTERPRISE":
        return ModelTier.ENTERPRISE

    logger.warning("Unexpected plan code '%s'; defaulting to FREEMIUM tier", plan_code)
    return ModelTier.FREEMIUM


def get_latest_price(symbol: str) -> tuple[float, float | None]:
    """
    Return a fake latest price via random walk and the previous price.

    TODO: replace with real market data / broker feed.
    """

    previous_price = _price_state.get(symbol)
    base_price = previous_price if previous_price is not None else 100.0
    epsilon = random.gauss(0, 0.001)  # small driftless random walk
    new_price = max(base_price * (1 + epsilon), 0.01)
    _price_state[symbol] = new_price
    return new_price, previous_price


def build_features(symbol: str, price: float, previous_price: float | None) -> dict[str, Any]:
    """Construct a minimal feature set for model inference."""

    if previous_price and previous_price > 0:
        return_1 = math.log(price / previous_price)
    else:
        return_1 = 0.0

    features = {
        "price": price,
        "return_1": return_1,
        "symbol_hash": hash(symbol) % 1000,
    }
    logger.debug("Built features for %s: %s", symbol, features)
    return features


def map_prediction_to_action(score: float | Any) -> str:
    """
    Map model output to a trading action.

    Assumes higher scores indicate more bullish signals (score in [0,1]).
    """

    try:
        numeric_score = float(score)
    except Exception:  # noqa: BLE001
        logger.warning("Non-numeric prediction output %s; defaulting to HOLD", score)
        return "HOLD"

    if numeric_score > 0.6:
        return "BUY"
    if numeric_score < 0.4:
        return "SELL"
    return "HOLD"


async def one_iteration() -> int:
    """Execute a single trading loop iteration."""

    if not settings.ENABLE_LIVE_TRADING and not settings.ENABLE_PAPER_TRADING:
        logger.info("Trading disabled (live & paper both off); skipping iteration.")
        return 0

    mode = "PAPER MODE" if settings.ENABLE_PAPER_TRADING and not settings.ENABLE_LIVE_TRADING else "LIVE/PAPER MIX"
    logger.info("Starting trading iteration (%s)", mode)
    logger.info("TODO: enforce MAX_DAILY_LOSS_PCT per user (currently %s)", settings.MAX_DAILY_LOSS_PCT)

    signals_created = 0
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(User, Plan).join(Plan, Plan.id == User.plan_id))
            rows = result.all()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to fetch users/plans: %s", exc)
            return 0

        for user, plan in rows:
            try:
                tier = plan_to_tier(plan.code if plan else None)

                price, previous_price = get_latest_price(TEST_SYMBOL)
                features = build_features(TEST_SYMBOL, price, previous_price)

                score = await predict_for_tier(session, tier, features, enterprise_slug=None)
                action = map_prediction_to_action(score if isinstance(score, Number) else score)

                try:
                    await enforce_plan_limits_for_signal(
                        session, user=user, plan=plan, symbol=TEST_SYMBOL, notional=price
                    )
                except PlanLimitExceeded as exc:
                    logger.info("Skipping signal for user %s due to plan limit: %s", user.id, exc.message)
                    continue

                signal = Signal(
                    user_id=user.id,
                    symbol=TEST_SYMBOL,
                    timestamp=datetime.now(timezone.utc),
                    signal_value=float(score) if isinstance(score, Number) else 0.0,
                    action=action,
                    model_name=f"champion:{tier.value}",
                )
                session.add(signal)
                signals_created += 1

                # TODO: integrate real broker orders or paper trade fills based on action.

            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to process user %s: %s", getattr(user, "id", "unknown"), exc)
                # Continue with next user without aborting the whole loop.
                continue

        try:
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Commit failed for trading iteration: %s", exc)
            return 0

    logger.info("Completed iteration; signals created: %s", signals_created)
    return signals_created


async def run_trading_loop() -> None:
    """Run the periodic trading loop indefinitely."""

    while True:
        try:
            await one_iteration()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Trading loop encountered an error: %s", exc)
        await asyncio.sleep(TRADING_LOOP_INTERVAL_SECONDS)


async def main() -> None:
    await run_trading_loop()


if __name__ == "__main__":
    asyncio.run(main())
