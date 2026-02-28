
from domain.coaches.coach import Coach
from domain.coaches.value_objects import Specialization
from domain.members.member import Member
from domain.members.value_objects import GoalType

_GOAL_TO_SPEC: dict[GoalType, set[Specialization]] = {
    GoalType.LOSE_WEIGHT: {Specialization.CARDIO, Specialization.NUTRITION},
    GoalType.BUILD_MUSCLE: {Specialization.STRENGTH, Specialization.CROSSFIT},
    GoalType.ENDURANCE: {Specialization.CARDIO, Specialization.CROSSFIT},
    GoalType.FLEXIBILITY: {Specialization.YOGA},
}


class CoachMatchingService:
    @staticmethod
    def find_best_coach(member: Member, coaches: list[Coach]) -> Coach | None:
        member_tier = member.membership.tier
        goal_specs: set[Specialization] = set()
        for goal in member.goals:
            goal_specs.update(_GOAL_TO_SPEC.get(goal.type, set()))

        candidates = [
            c for c in coaches
            if c.can_accept_client(member_tier)
            and bool(c.specializations & goal_specs)
        ]
        if not candidates:
            return None
        candidates.sort(
            key=lambda c: (
                -len(c.specializations & goal_specs),
                c.current_client_count,
            )
        )
        return candidates[0]
