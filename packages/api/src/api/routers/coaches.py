
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query

from api.schemas.coach_schemas import CoachCreate, CoachResponse
from application.coaches.coach_service import CoachService
from bootstrap.containers import Container

router = APIRouter(prefix="/coaches", tags=["coaches"])


@router.post("/", response_model=CoachResponse, status_code=201)
@inject
async def register_coach(
    body: CoachCreate,
    coach_service: CoachService = Depends(Provide[Container.coach_service]),
) -> CoachResponse:
    try:
        coach = await coach_service.register(
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            bio=body.bio,
            tier=body.tier,
            specializations=body.specializations,
            max_clients=body.max_clients,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return CoachResponse.from_domain(coach)


@router.get("/", response_model=list[CoachResponse])
@inject
async def list_coaches(
    specialization: str | None = Query(None),
    coach_service: CoachService = Depends(Provide[Container.coach_service]),
) -> list[CoachResponse]:
    coaches = await coach_service.find_available(specialization)
    return [CoachResponse.from_domain(c) for c in coaches]


@router.get("/match", response_model=CoachResponse | None)
@inject
async def match_coach_for_member(
    member_id: int = Query(...),
    coach_service: CoachService = Depends(Provide[Container.coach_service]),
) -> CoachResponse | None:
    try:
        coach = await coach_service.find_best_for_member(member_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return CoachResponse.from_domain(coach) if coach else None


@router.get("/{coach_id}", response_model=CoachResponse)
@inject
async def get_coach(
    coach_id: int,
    coach_service: CoachService = Depends(Provide[Container.coach_service]),
) -> CoachResponse:
    coach = await coach_service.get(coach_id)
    if coach is None:
        raise HTTPException(status_code=404, detail=f"Coach {coach_id} not found")
    return CoachResponse.from_domain(coach)


@router.delete("/{coach_id}", status_code=204)
@inject
async def delete_coach(
    coach_id: int,
    coach_service: CoachService = Depends(Provide[Container.coach_service]),
) -> None:
    await coach_service.delete(coach_id)
