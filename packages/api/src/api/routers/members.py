
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from api.schemas.member_schemas import GoalCreate, MemberCreate, MemberResponse
from application.members.member_service import MemberService
from bootstrap.containers import Container

router = APIRouter(prefix="/members", tags=["members"])


@router.post("/", response_model=MemberResponse, status_code=201)
@inject
async def register_member(
    body: MemberCreate,
    member_service: MemberService = Depends(Provide[Container.member_service]),
) -> MemberResponse:
    try:
        member = await member_service.register(
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            phone=body.phone,
            fitness_level=body.fitness_level,
            membership_tier=body.membership_tier,
            membership_valid_until=body.membership_valid_until,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return MemberResponse.from_domain(member)


@router.get("/", response_model=list[MemberResponse])
@inject
async def list_members(
    member_service: MemberService = Depends(Provide[Container.member_service]),
) -> list[MemberResponse]:
    members = await member_service.get_all()
    return [MemberResponse.from_domain(m) for m in members]


@router.get("/{member_id}", response_model=MemberResponse)
@inject
async def get_member(
    member_id: int,
    member_service: MemberService = Depends(Provide[Container.member_service]),
) -> MemberResponse:
    member = await member_service.get(member_id)
    return MemberResponse.from_domain(member)


@router.post("/{member_id}/goals", response_model=MemberResponse, status_code=201)
@inject
async def add_goal(
    member_id: int,
    body: GoalCreate,
    member_service: MemberService = Depends(Provide[Container.member_service]),
) -> MemberResponse:
    try:
        member = await member_service.add_goal(
            member_id=member_id,
            goal_type=body.goal_type,
            description=body.description,
            target_date=body.target_date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return MemberResponse.from_domain(member)


@router.delete("/{member_id}", status_code=204)
@inject
async def delete_member(
    member_id: int,
    member_service: MemberService = Depends(Provide[Container.member_service]),
) -> None:
    await member_service.delete(member_id)
