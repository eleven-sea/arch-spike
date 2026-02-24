from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from domain.members.value_objects import GoalId, GoalType


@dataclass
class FitnessGoal:
    type: GoalType
    description: str
    target_date: date
    achieved: bool = False
    id: GoalId | None = None

    def __post_init__(self) -> None:
        if self.target_date <= date.today():
            raise ValueError("target_date must be in the future")

    def mark_achieved(self) -> None:
        self.achieved = True
