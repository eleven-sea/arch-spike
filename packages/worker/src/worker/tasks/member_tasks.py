from dependency_injector.wiring import Provide, inject

from application.members.member_service import MemberService
from bootstrap.containers import Container
from infrastructure.taskiq.broker import broker


@broker.task
@inject
async def log_member_activity(
    member_id: int,
    member_service: MemberService = Provide[Container.member_service],
) -> None:
    member = await member_service.get(member_id)
    if member is None:
        return
    print(f"member from worker: {member}")
