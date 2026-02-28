
from typing import Self

from pydantic import BaseModel

from domain.coaches.coach import Coach


class CoachCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    bio: str = ""
    tier: str = "STANDARD"
    specializations: list[str] = []
    max_clients: int = 10


class CoachResponse(BaseModel):
    id: int | None
    first_name: str
    last_name: str
    email: str
    bio: str
    tier: str
    specializations: list[str]
    max_clients: int
    current_client_count: int

    model_config = {"from_attributes": True}

    @classmethod
    def from_domain(cls, c: Coach) -> Self:
        return cls(
            id=c.id,
            first_name=c.name.first_name,
            last_name=c.name.last_name,
            email=c.email.value,
            bio=c.bio,
            tier=c.tier.value,
            specializations=[s.value for s in c.specializations],
            max_clients=c.max_clients,
            current_client_count=c.current_client_count,
        )
