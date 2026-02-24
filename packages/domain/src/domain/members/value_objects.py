from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

MemberId = int
GoalId = int


class FitnessLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class MembershipTier(str, Enum):
    FREE = "FREE"
    PREMIUM = "PREMIUM"
    VIP = "VIP"


class GoalType(str, Enum):
    LOSE_WEIGHT = "LOSE_WEIGHT"
    BUILD_MUSCLE = "BUILD_MUSCLE"
    ENDURANCE = "ENDURANCE"
    FLEXIBILITY = "FLEXIBILITY"


@dataclass(frozen=True)
class Membership:
    tier: MembershipTier
    valid_until: date

    def is_active(self, as_of: date | None = None) -> bool:
        check = as_of or date.today()
        return self.valid_until >= check
