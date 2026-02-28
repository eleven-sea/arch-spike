
from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

MemberId = int
GoalId = int


class FitnessLevel(StrEnum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class MembershipTier(StrEnum):
    FREE = "FREE"
    PREMIUM = "PREMIUM"
    VIP = "VIP"


class GoalType(StrEnum):
    LOSE_WEIGHT = "LOSE_WEIGHT"
    BUILD_MUSCLE = "BUILD_MUSCLE"
    ENDURANCE = "ENDURANCE"
    FLEXIBILITY = "FLEXIBILITY"


class Membership(BaseModel):
    model_config = ConfigDict(frozen=True)

    tier: MembershipTier
    valid_until: date

    def is_active(self, as_of: date | None = None) -> bool:
        check = as_of or date.today()
        return self.valid_until >= check
