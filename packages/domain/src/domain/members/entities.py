
from datetime import date

from pydantic import BaseModel

from domain.members.value_objects import GoalId, GoalType


class FitnessGoal(BaseModel):
    type: GoalType
    description: str
    target_date: date
    achieved: bool = False
    id: GoalId | None = None

    def mark_achieved(self) -> None:
        self.achieved = True
