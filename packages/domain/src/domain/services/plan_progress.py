
from domain.plans.training_plan import TrainingPlan
from domain.plans.value_objects import SessionStatus


class PlanProgressService:
    @staticmethod
    def completion_pct(plan: TrainingPlan) -> float:
        if not plan.sessions:
            return 0.0
        done = sum(
            1
            for s in plan.sessions
            if s.status in (SessionStatus.COMPLETED, SessionStatus.SKIPPED)
        )
        return round(done / len(plan.sessions) * 100, 2)
