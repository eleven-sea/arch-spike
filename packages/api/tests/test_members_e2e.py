"""E2E tests for /members endpoints."""

from datetime import date, timedelta


def _member_payload(**overrides):
    payload = {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "email": "jan@test.com",
        "phone": "+48123456789",
        "fitness_level": "BEGINNER",
        "membership_tier": "FREE",
        "membership_valid_until": (date.today() + timedelta(days=30)).isoformat(),
    }
    payload.update(overrides)
    return payload


class TestRegisterMember:
    async def test_creates_member_returns_201(self, client):
        resp = await client.post("/members/", json=_member_payload())
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "jan@test.com"
        assert data["id"] is not None

    async def test_invalid_email_returns_422(self, client):
        resp = await client.post("/members/", json=_member_payload(email="not-an-email"))
        assert resp.status_code == 422

    async def test_duplicate_email_returns_422(self, client):
        await client.post("/members/", json=_member_payload())
        resp = await client.post("/members/", json=_member_payload())
        assert resp.status_code == 422


class TestListMembers:
    async def test_returns_empty_list(self, client):
        resp = await client.get("/members/")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_returns_all_members(self, client):
        await client.post("/members/", json=_member_payload())
        await client.post("/members/", json=_member_payload(email="b@test.com"))
        resp = await client.get("/members/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestGetMember:
    async def test_returns_member(self, client):
        created = (await client.post("/members/", json=_member_payload())).json()
        resp = await client.get(f"/members/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    async def test_not_found_returns_404(self, client):
        resp = await client.get("/members/99999")
        assert resp.status_code == 404


class TestAddGoal:
    async def test_adds_goal(self, client):
        member = (await client.post("/members/", json=_member_payload())).json()
        goal_payload = {
            "goal_type": "LOSE_WEIGHT",
            "description": "Lose 5 kg",
            "target_date": (date.today() + timedelta(days=60)).isoformat(),
        }
        resp = await client.post(f"/members/{member['id']}/goals", json=goal_payload)
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["goals"]) == 1
        assert data["goals"][0]["type"] == "LOSE_WEIGHT"


class TestDeleteMember:
    async def test_deletes_member(self, client):
        member = (await client.post("/members/", json=_member_payload())).json()
        resp = await client.delete(f"/members/{member['id']}")
        assert resp.status_code == 204
        get_resp = await client.get(f"/members/{member['id']}")
        assert get_resp.status_code == 404
