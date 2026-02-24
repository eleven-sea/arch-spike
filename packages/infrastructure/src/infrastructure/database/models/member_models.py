from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import Base


class FitnessGoalORM(Base):
    __tablename__ = "fitness_goals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    achieved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class MemberORM(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    fitness_level: Mapped[str] = mapped_column(String(20), nullable=False)
    membership_tier: Mapped[str] = mapped_column(String(20), nullable=False)
    membership_valid_until: Mapped[date] = mapped_column(Date, nullable=False)
    active_plan_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    goals: Mapped[List[FitnessGoalORM]] = relationship(
        "FitnessGoalORM",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
