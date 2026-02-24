from __future__ import annotations

from application.core.logger import ILogger
from application.core.ports import IExerciseClient
from infrastructure.clients.exercise_client import WgerClient


class WgerAdapter(IExerciseClient):
    def __init__(self, client: WgerClient, app_logger: ILogger) -> None:
        self._client = client
        self._log = app_logger.get_logger(__name__)

    async def get_exercise(self, exercise_id: str) -> dict | None:
        try:
            response = await self._client.client.get(f"/exercise/{exercise_id}/")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            self._log.warning("wger get_exercise(%s) failed: %s", exercise_id, exc)
            return None

    async def search_exercises(self, name: str) -> list[dict]:
        try:
            response = await self._client.client.get(
                "/exercise/search/",
                params={"term": name, "language": "english", "format": "json"},
            )
            response.raise_for_status()
            data = response.json()
            suggestions = data.get("suggestions", [])
            results = []
            for s in suggestions:
                results.append(
                    {
                        "exercise_id": str(s.get("data", {}).get("id", "")),
                        "name": s.get("value", name),
                    }
                )
            return results
        except Exception as exc:
            self._log.warning("wger search_exercises(%r) failed: %s", name, exc)
            return []
