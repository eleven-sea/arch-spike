
from domain.shared.events import ApplicationEvent


class CoachRegistered(ApplicationEvent):
    coach_id: int | None
    email: str
    full_name: str
