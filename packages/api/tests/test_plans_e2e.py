"""E2E tests for /plans endpoints."""

from datetime import date, timedelta

import pytest


def _member_payload(email: str = "jan@test.com"):
    return {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "email": email,
        "phone": "+48123456789",
        "fitness_level": "BEGINNER",
        "membership_tier": "FREE",
        "membership_valid_until": (date.today() + timedelta(days=30)).isoformat(),
    }


def _coach_payload(email: str = "anna@gym.com"):
    return {
        "first_name": "Anna",
        "last_name": "Trainer",
        "email": email,
        "bio": "Trainer",
        "tier": "STANDARD",
        "specializations": ["STRENGTH"],
        "max_clients": 10,
    }


@pytest.fixture()
async def member_id(client):
    r = await client.post("/members/", json=_member_payload())
    return r.json()["id"]


@pytest.fixture()
async def coach_id(client):
    r = await client.post("/coaches/", json=_coach_payload())
    return r.json()["id"]


@pytest.fixture()
async def draft_plan(client, member_id, coach_id):
    payload = {
        "member_id": member_id,
        "coach_id": coach_id,
        "name": "Test Plan",
        "starts_at": date.today().isoformat(),
        "ends_at": (date.today() + timedelta(weeks=4)).isoformat(),
    }
    r = await client.post("/plans/", json=payload)
    assert r.status_code == 201
    return r.json()


class TestCreatePlan:
    async def test_creates_draft_plan(self, draft_plan):
        assert draft_plan["status"] == "DRAFT"
        assert draft_plan["id"] is not None

    async def test_unknown_member_returns_422(self, client, coach_id):
        payload = {
            "member_id": 9999,
            "coach_id": coach_id,
            "name": "x",
            "starts_at": date.today().isoformat(),
            "ends_at": (date.today() + timedelta(weeks=4)).isoformat(),
        }
        resp = await client.post("/plans/", json=payload)
        assert resp.status_code == 422


class TestAddSession:
    async def test_add_session_to_draft(self, client, draft_plan):
        payload = {
            "name": "Leg Day",
            "scheduled_date": (date.today() + timedelta(days=1)).isoformat(),
            "exercises": [
                {"name": "Squat", "sets": 3, "reps": 10, "rest_seconds": 60}
            ],
        }
        resp = await client.post(f"/plans/{draft_plan['id']}/sessions", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["name"] == "Leg Day"


class TestActivatePlan:
    async def test_activates_draft_plan(self, client, draft_plan):
        resp = await client.post(f"/plans/{draft_plan['id']}/activate")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ACTIVE"


class TestCompleteSession:
    async def test_complete_session_auto_completes_plan(
        self, client, draft_plan
    ):
        plan_id = draft_plan["id"]

        sess_payload = {
            "name": "Day 1",
            "scheduled_date": (date.today() + timedelta(days=1)).isoformat(),
            "exercises": [{"name": "Squat", "sets": 3, "reps": 10, "rest_seconds": 60}],
        }
        plan = (await client.post(f"/plans/{plan_id}/sessions", json=sess_payload)).json()

        plan = (await client.post(f"/plans/{plan_id}/activate")).json()
        assert plan["status"] == "ACTIVE"

        session_id = plan["sessions"][0]["id"]
        resp = await client.post(
            f"/plans/{plan_id}/sessions/{session_id}/complete",
            json={"notes": "Felt great!"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["sessions"][0]["status"] == "COMPLETED"
        assert data["status"] == "COMPLETED"  # auto-completed


class TestPlanProgress:
    async def test_empty_plan_is_zero(self, client, draft_plan):
        resp = await client.get(f"/plans/{draft_plan['id']}/progress")
        assert resp.status_code == 200
        assert resp.json()["completion_pct"] == 0.0

    async def test_progress_after_completing_session(self, client, draft_plan):
        plan_id = draft_plan["id"]
        sess_payload = {
            "name": "Day 1",
            "scheduled_date": (date.today() + timedelta(days=1)).isoformat(),
            "exercises": [],
        }
        await client.post(f"/plans/{plan_id}/sessions", json=sess_payload)
        plan = (await client.post(f"/plans/{plan_id}/activate")).json()
        session_id = plan["sessions"][0]["id"]
        await client.post(
            f"/plans/{plan_id}/sessions/{session_id}/complete", json={}
        )
        resp = await client.get(f"/plans/{plan_id}/progress")
        assert resp.status_code == 200
        assert resp.json()["completion_pct"] == 100.0

    async def test_unknown_plan_returns_404(self, client):
        resp = await client.get("/plans/99999/progress")
        assert resp.status_code == 404
