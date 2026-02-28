from datetime import date
from typing import ClassVar, override

from sqlmodel import Field, Relationship

from infrastructure.database.base import Base


class FitnessGoalORM(Base, table=True):
    __tablename__: ClassVar[str] = "fitness_goals"  # pyright: ignore[reportIncompatibleVariableOverride]
    id: int | None = Field(default=None, primary_key=True)
    member_id: int = Field(foreign_key="members.id")
    type: str = Field(max_length=50)
    description: str = Field(max_length=500)
    target_date: date
    achieved: bool = Field(default=False)

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None


class MemberORM(Base, table=True):
    __tablename__: ClassVar[str] = "members"  # pyright: ignore[reportIncompatibleVariableOverride]
    id: int | None = Field(default=None, primary_key=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: str = Field(unique=True, max_length=255)
    phone: str = Field(max_length=30)
    fitness_level: str = Field(max_length=20)
    membership_tier: str = Field(max_length=20)
    membership_valid_until: date
    active_plan_id: int | None = Field(default=None)
    goals: list[FitnessGoalORM] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None
