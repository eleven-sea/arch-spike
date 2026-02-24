from __future__ import annotations

import logging

from domain.members.entities import FitnessGoal
from domain.members.member import Member
from domain.members.repositories import IMemberRepository
from domain.members.value_objects import FitnessLevel, GoalType, Membership, MembershipTier
from application.core.events import IEventDispatcher
from application.core.logger import ILogger


class MemberService:
    def __init__(
        self,
        member_repo: IMemberRepository,
        dispatcher: IEventDispatcher,
        app_logger: ILogger,
    ) -> None:
        self._repo = member_repo
        self._dispatcher = dispatcher
        self._logger = app_logger

    async def register(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        fitness_level: str,
        membership_tier: str = "FREE",
        membership_valid_until: str | None = None,
    ) -> Member:
        from datetime import date, timedelta

        logger = self._logger.get_logger(__name__)

        if await self._repo.get_by_email(email) is not None:
            raise ValueError(f"Email {email!r} already registered")

        valid_until = (
            date.fromisoformat(membership_valid_until)
            if membership_valid_until
            else date.today() + timedelta(days=30)
        )
        member = Member.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            fitness_level=FitnessLevel(fitness_level),
            membership=Membership(
                tier=MembershipTier(membership_tier),
                valid_until=valid_until,
            ),
        )
        saved = await self._repo.save(member)
        logger.info("Member registered: %s (id=%s)", saved.email.value, saved.id)

        for event in member.pull_events():
            self._dispatcher.run_in_background(event)

        return saved

    async def get(self, member_id: int) -> Member | None:
        return await self._repo.get_by_id(member_id)

    async def get_all(self) -> list[Member]:
        return await self._repo.get_all()

    async def add_goal(
        self,
        member_id: int,
        goal_type: str,
        description: str,
        target_date: str,
    ) -> Member:
        from datetime import date

        member = await self._repo.get_by_id(member_id)
        if member is None:
            raise ValueError(f"Member {member_id} not found")

        goal = FitnessGoal(
            type=GoalType(goal_type),
            description=description,
            target_date=date.fromisoformat(target_date),
        )
        member.add_goal(goal)
        saved = await self._repo.save(member)

        for event in saved.pull_events():
            self._dispatcher.run_in_background(event)

        return saved

    async def achieve_goal(self, member_id: int, goal_id: int) -> Member:
        member = await self._repo.get_by_id(member_id)
        if member is None:
            raise ValueError(f"Member {member_id} not found")

        member.achieve_goal(goal_id)
        saved = await self._repo.save(member)

        for event in saved.pull_events():
            self._dispatcher.run_in_background(event)

        return saved

    async def delete(self, member_id: int) -> None:
        await self._repo.delete(member_id)
