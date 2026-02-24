from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel


class MemberCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    fitness_level: str  # BEGINNER / INTERMEDIATE / ADVANCED
    membership_tier: str = "FREE"
    membership_valid_until: Optional[str] = None  # ISO date string


class GoalCreate(BaseModel):
    goal_type: str       # LOSE_WEIGHT / BUILD_MUSCLE / ENDURANCE / FLEXIBILITY
    description: str
    target_date: str     # ISO date string


class GoalResponse(BaseModel):
    id: Optional[int]
    type: str
    description: str
    target_date: date
    achieved: bool

    model_config = {"from_attributes": True}


class MemberResponse(BaseModel):
    id: Optional[int]
    first_name: str
    last_name: str
    email: str
    phone: str
    fitness_level: str
    membership_tier: str
    membership_valid_until: date
    active_plan_id: Optional[int]
    goals: list[GoalResponse]

    model_config = {"from_attributes": True}

    @classmethod
    def from_domain(cls, m) -> "MemberResponse":
        return cls(
            id=m.id,
            first_name=m.name.first_name,
            last_name=m.name.last_name,
            email=m.email.value,
            phone=m.phone.value,
            fitness_level=m.fitness_level.value,
            membership_tier=m.membership.tier.value,
            membership_valid_until=m.membership.valid_until,
            active_plan_id=m.active_plan_id,
            goals=[
                GoalResponse(
                    id=g.id,
                    type=g.type.value,
                    description=g.description,
                    target_date=g.target_date,
                    achieved=g.achieved,
                )
                for g in m.goals
            ],
        )
