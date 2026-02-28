from dependency_injector.wiring import Provide, inject

from application.members.member_service import MemberService
from bootstrap.broker import broker
from bootstrap.containers import Container
from domain.members.member import Member


@broker.task
@inject
async def log_member_activity(
    member_id: int,
    member_service: MemberService = Provide[Container.member_service],
) -> None:
    member: Member = await member_service.get(member_id)
    print(f"member from worker: {member}")
