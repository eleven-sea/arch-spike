
import httpx


class WgerClient:
    """HTTP client for the wger.de exercise API."""

    def __init__(self, base_url: str = "https://wger.de/api/v2", timeout: float = 10.0) -> None:
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={"Accept": "application/json"},
        )

    async def close(self) -> None:
        await self.client.aclose()
