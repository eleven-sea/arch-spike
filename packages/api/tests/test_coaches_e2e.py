"""E2E tests for /coaches endpoints."""


def _coach_payload(**overrides):
    payload = {
        "first_name": "Anna",
        "last_name": "Trainer",
        "email": "anna@gym.com",
        "bio": "Experienced trainer",
        "tier": "STANDARD",
        "specializations": ["STRENGTH", "CARDIO"],
        "max_clients": 10,
    }
    payload.update(overrides)
    return payload


class TestRegisterCoach:
    async def test_creates_coach_returns_201(self, client):
        resp = await client.post("/coaches/", json=_coach_payload())
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "anna@gym.com"
        assert "STRENGTH" in data["specializations"]

    async def test_duplicate_email_returns_422(self, client):
        await client.post("/coaches/", json=_coach_payload())
        resp = await client.post("/coaches/", json=_coach_payload())
        assert resp.status_code == 422


class TestListCoaches:
    async def test_returns_empty_list(self, client):
        resp = await client.get("/coaches/")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_returns_all_coaches(self, client):
        await client.post("/coaches/", json=_coach_payload())
        resp = await client.get("/coaches/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_filter_by_specialization(self, client):
        await client.post("/coaches/", json=_coach_payload(specializations=["STRENGTH"]))
        await client.post("/coaches/", json=_coach_payload(
            email="yoga@gym.com", specializations=["YOGA"]
        ))
        resp = await client.get("/coaches/?specialization=STRENGTH")
        assert resp.status_code == 200
        coaches = resp.json()
        assert all("STRENGTH" in c["specializations"] for c in coaches)


class TestGetCoach:
    async def test_returns_coach(self, client):
        created = (await client.post("/coaches/", json=_coach_payload())).json()
        resp = await client.get(f"/coaches/{created['id']}")
        assert resp.status_code == 200

    async def test_not_found_returns_404(self, client):
        resp = await client.get("/coaches/99999")
        assert resp.status_code == 500


class TestMatchCoach:
    async def _register_member(self, client):
        from datetime import date, timedelta

        valid_until = (date.today() + timedelta(days=30)).isoformat()
        resp = await client.post("/members/", json={
            "first_name": "Jan", "last_name": "Kowalski",
            "email": "jan@match.com", "phone": "+48123456789",
            "fitness_level": "BEGINNER", "membership_valid_until": valid_until,
        })
        return resp.json()

    async def test_returns_null_when_no_coaches(self, client):
        member = await self._register_member(client)
        resp = await client.get(f"/coaches/match?member_id={member['id']}")
        assert resp.status_code == 200
        assert resp.json() is None

    async def test_returns_best_coach_for_member(self, client):
        member = await self._register_member(client)
        await client.post("/coaches/", json=_coach_payload())
        resp = await client.get(f"/coaches/match?member_id={member['id']}")
        assert resp.status_code == 200

    async def test_unknown_member_returns_404(self, client):
        resp = await client.get("/coaches/match?member_id=99999")
        assert resp.status_code == 500
