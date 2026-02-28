from datetime import date
from typing import ClassVar, override

from sqlmodel import Field, Relationship

from infrastructure.database.base import Base


class CertificationORM(Base, table=True):
    __tablename__: ClassVar[str] = "certifications"  # pyright: ignore[reportIncompatibleVariableOverride]
    id: int | None = Field(default=None, primary_key=True)
    coach_id: int = Field(foreign_key="coaches.id")
    name: str = Field(max_length=200)
    issuing_body: str = Field(max_length=200)
    issued_at: date
    expires_at: date | None = Field(default=None)

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None


class AvailabilitySlotORM(Base, table=True):
    __tablename__: ClassVar[str] = "availability_slots"  # pyright: ignore[reportIncompatibleVariableOverride]
    id: int | None = Field(default=None, primary_key=True)
    coach_id: int = Field(foreign_key="coaches.id")
    day: str = Field(max_length=3)
    start_hour: int
    end_hour: int

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None


class CoachSpecializationORM(Base, table=True):
    __tablename__: ClassVar[str] = "coach_spec_rows"  # pyright: ignore[reportIncompatibleVariableOverride]
    id: int | None = Field(default=None, primary_key=True)
    coach_id: int = Field(foreign_key="coaches.id")
    specialization: str = Field(max_length=30)

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None


class CoachORM(Base, table=True):
    __tablename__: ClassVar[str] = "coaches"  # pyright: ignore[reportIncompatibleVariableOverride]
    id: int | None = Field(default=None, primary_key=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: str = Field(unique=True, max_length=255)
    bio: str = Field(default="", max_length=2000)
    tier: str = Field(max_length=20)
    max_clients: int = Field(default=10)
    current_client_count: int = Field(default=0)
    certifications: list[CertificationORM] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    available_slots: list[AvailabilitySlotORM] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    specializations: list[CoachSpecializationORM] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None
