
from datetime import date
from typing import Self

from pydantic import BaseModel

from domain.members.member import Member


class MemberCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    fitness_level: str
    membership_tier: str = "FREE"
    membership_valid_until: str | None = None


class GoalCreate(BaseModel):
    goal_type: str
    description: str
    target_date: str


class GoalResponse(BaseModel):
    id: int | None
    type: str
    description: str
    target_date: date
    achieved: bool

    model_config = {"from_attributes": True}


class MemberResponse(BaseModel):
    id: int | None
    first_name: str
    last_name: str
    email: str
    phone: str
    fitness_level: str
    membership_tier: str
    membership_valid_until: date
    active_plan_id: int | None
    goals: list[GoalResponse]

    model_config = {"from_attributes": True}

    @classmethod
    def from_domain(cls, m: Member) -> Self:
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
