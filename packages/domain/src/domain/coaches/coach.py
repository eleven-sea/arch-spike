
from typing import Self

from pydantic import BaseModel, PrivateAttr

from domain.coaches.entities import AvailabilitySlot, Certification
from domain.coaches.value_objects import CoachTier, Specialization
from domain.members.value_objects import MembershipTier
from domain.shared.events import ApplicationEvent
from domain.shared.value_objects import Email, FullName


class Coach(BaseModel):
    name: FullName
    email: Email
    bio: str
    tier: CoachTier
    specializations: frozenset[Specialization]
    max_clients: int
    current_client_count: int = 0
    certifications: list[Certification] = []
    available_slots: list[AvailabilitySlot] = []
    id: int | None = None

    _events: list[ApplicationEvent] = PrivateAttr(default_factory=list)  # pyright: ignore[reportUnknownVariableType]

    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str,
        email: str,
        bio: str,
        tier: CoachTier,
        specializations: frozenset[Specialization],
        max_clients: int,
    ) -> Self:
        from domain.coaches.events import CoachRegistered

        coach = cls(
            name=FullName(first_name=first_name, last_name=last_name),
            email=Email(value=email),
            bio=bio,
            tier=tier,
            specializations=specializations,
            max_clients=max_clients,
        )
        coach._events.append(
            CoachRegistered(
                coach_id=coach.id,
                email=email,
                full_name=coach.name.full,
            )
        )
        return coach

    def can_accept_client(self, member_tier: MembershipTier | None = None) -> bool:
        if self.current_client_count >= self.max_clients:
            return False
        if self.tier == CoachTier.VIP and member_tier != MembershipTier.VIP:
            return False
        return True

    def accept_client(self) -> None:
        if self.current_client_count >= self.max_clients:
            raise ValueError("Coach is at full capacity")
        self.current_client_count += 1

    def release_client(self) -> None:
        if self.current_client_count > 0:
            self.current_client_count -= 1

    def add_certification(self, cert: Certification) -> None:
        self.certifications.append(cert)

    def add_availability_slot(self, slot: AvailabilitySlot) -> None:
        self.available_slots.append(slot)

    def pull_events(self) -> list[ApplicationEvent]:
        events, self._events = self._events, []
        return events
