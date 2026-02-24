from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide

from bootstrap.containers import Container
from application.plans.plan_service import TrainingPlanService
from api.schemas.plan_schemas import (
    CompleteSession,
    PlanCreate,
    PlanProgressResponse,
    PlanResponse,
    SessionCreate,
)

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("/", response_model=PlanResponse, status_code=201)
@inject
async def create_plan(
    body: PlanCreate,
    plan_service: TrainingPlanService = Depends(Provide[Container.plan_service]),
) -> PlanResponse:
    try:
        plan = await plan_service.create_plan(
            member_id=body.member_id,
            coach_id=body.coach_id,
            name=body.name,
            starts_at=body.starts_at,
            ends_at=body.ends_at,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return PlanResponse.from_domain(plan)


@router.post("/{plan_id}/activate", response_model=PlanResponse)
@inject
async def activate_plan(
    plan_id: int,
    plan_service: TrainingPlanService = Depends(Provide[Container.plan_service]),
) -> PlanResponse:
    try:
        plan = await plan_service.activate_plan(plan_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return PlanResponse.from_domain(plan)


@router.get("/{plan_id}", response_model=PlanResponse)
@inject
async def get_plan(
    plan_id: int,
    plan_service: TrainingPlanService = Depends(Provide[Container.plan_service]),
) -> PlanResponse:
    plan = await plan_service.get(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    return PlanResponse.from_domain(plan)


@router.get("/{plan_id}/progress", response_model=PlanProgressResponse)
@inject
async def get_plan_progress(
    plan_id: int,
    plan_service: TrainingPlanService = Depends(Provide[Container.plan_service]),
) -> PlanProgressResponse:
    try:
        pct = await plan_service.get_progress(plan_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return PlanProgressResponse(plan_id=plan_id, completion_pct=pct)


@router.post("/{plan_id}/sessions", response_model=PlanResponse, status_code=201)
@inject
async def add_session(
    plan_id: int,
    body: SessionCreate,
    plan_service: TrainingPlanService = Depends(Provide[Container.plan_service]),
) -> PlanResponse:
    try:
        plan = await plan_service.add_session(
            plan_id=plan_id,
            session_name=body.name,
            scheduled_date=body.scheduled_date,
            exercises=[ex.model_dump() for ex in body.exercises],
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return PlanResponse.from_domain(plan)


@router.post("/{plan_id}/sessions/{session_id}/complete", response_model=PlanResponse)
@inject
async def complete_session(
    plan_id: int,
    session_id: int,
    body: CompleteSession,
    plan_service: TrainingPlanService = Depends(Provide[Container.plan_service]),
) -> PlanResponse:
    try:
        plan = await plan_service.complete_session(
            plan_id=plan_id,
            session_id=session_id,
            notes=body.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return PlanResponse.from_domain(plan)
