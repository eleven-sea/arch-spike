from datetime import date
from typing import override

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import Base


class CertificationORM(Base):
    __tablename__ = "certifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    coach_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("coaches.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    issuing_body: Mapped[str] = mapped_column(String(200), nullable=False)
    issued_at: Mapped[date] = mapped_column(Date, nullable=False)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None  # pyright: ignore[reportUnnecessaryComparison]


class AvailabilitySlotORM(Base):
    __tablename__ = "availability_slots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    coach_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("coaches.id", ondelete="CASCADE"), nullable=False)
    day: Mapped[str] = mapped_column(String(3), nullable=False)
    start_hour: Mapped[int] = mapped_column(Integer, nullable=False)
    end_hour: Mapped[int] = mapped_column(Integer, nullable=False)

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None  # pyright: ignore[reportUnnecessaryComparison]


class CoachSpecializationORM(Base):
    __tablename__ = "coach_spec_rows"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    coach_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("coaches.id", ondelete="CASCADE"), nullable=False)
    specialization: Mapped[str] = mapped_column(String(30), nullable=False)

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None  # pyright: ignore[reportUnnecessaryComparison]


class CoachORM(Base):
    __tablename__ = "coaches"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    bio: Mapped[str] = mapped_column(String(2000), nullable=False, default="")
    tier: Mapped[str] = mapped_column(String(20), nullable=False)
    max_clients: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    current_client_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    certifications: Mapped[list[CertificationORM]] = relationship(
        "CertificationORM",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    available_slots: Mapped[list[AvailabilitySlotORM]] = relationship(
        "AvailabilitySlotORM",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    specializations: Mapped[list[CoachSpecializationORM]] = relationship(
        "CoachSpecializationORM",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None  # pyright: ignore[reportUnnecessaryComparison]
