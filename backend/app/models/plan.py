from dataclasses import dataclass

from app.models.user import PlanEnum


@dataclass(frozen=True)
class Plan:
    name: PlanEnum
    features: list[str]


AVAILABLE_PLANS: list[Plan] = [
    Plan(
        name=PlanEnum.free,
        features=["Paper trading", "Baseline signals", "Chat explanations"],
    ),
    Plan(
        name=PlanEnum.pro,
        features=["Broker connectivity", "Enhanced signals", "Priority chat"],
    ),
    Plan(
        name=PlanEnum.enterprise,
        features=["Multi-broker", "Advanced ML models", "Custom reporting"],
    ),
]
