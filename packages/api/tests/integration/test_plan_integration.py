"""Integration tests — TrainingPlan aggregate against real PostgreSQL."""

from datetime import date, timedelta

import pytest


async def _register_member(svc, email: str = "jan@test.com"):
    valid_until = (date.today() + timedelta(days=30)).isoformat()
    return await svc.register(
        first_name="Jan",
        last_name="Kowalski",
        email=email,
        phone="+48123456789",
        fitness_level="BEGINNER",
        membership_valid_until=valid_until,
    )


async def _register_coach(svc, email: str = "anna@gym.com"):
    return await svc.register(
        first_name="Anna",
        last_name="Trainer",
        email=email,
        bio="Trainer",
        tier="STANDARD",
        specializations=["STRENGTH"],
        max_clients=10,
    )


class TestPlanIntegration:
    async def test_full_plan_lifecycle(
        self, plan_service, member_service, coach_service
    ):
        member = await _register_member(member_service)
        coach = await _register_coach(coach_service)

        plan = await plan_service.create_plan(
            member_id=member.id,
            coach_id=coach.id,
            name="Integration Plan",
            starts_at=date.today().isoformat(),
            ends_at=(date.today() + timedelta(weeks=4)).isoformat(),
        )
        assert plan.status.value == "DRAFT"

        plan = await plan_service.add_session(
            plan_id=plan.id,
            session_name="Day 1",
            scheduled_date=(date.today() + timedelta(days=1)).isoformat(),
            exercises=[{"name": "Squat", "sets": 3, "reps": 10, "rest_seconds": 60}],
        )
        assert len(plan.sessions) == 1

        plan = await plan_service.activate_plan(plan.id)
        assert plan.status.value == "ACTIVE"

        session_id = plan.sessions[0].id
        plan = await plan_service.complete_session(plan.id, session_id)
        assert plan.sessions[0].status.value == "COMPLETED"
        assert plan.status.value == "COMPLETED"

    async def test_cannot_complete_session_on_draft(
        self, plan_service, member_service
    ):
        member = await _register_member(member_service, "m2@test.com")
        plan = await plan_service.create_plan(
            member_id=member.id,
            coach_id=1,
            name="Draft Plan",
            starts_at=date.today().isoformat(),
            ends_at=(date.today() + timedelta(weeks=4)).isoformat(),
        )
        plan = await plan_service.add_session(
            plan_id=plan.id,
            session_name="Day 1",
            scheduled_date=(date.today() + timedelta(days=1)).isoformat(),
            exercises=[],
        )
        session_id = plan.sessions[0].id
        with pytest.raises(ValueError):
            await plan_service.complete_session(plan.id, session_id)
