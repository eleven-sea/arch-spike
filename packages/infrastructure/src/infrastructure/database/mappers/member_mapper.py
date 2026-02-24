from __future__ import annotations

from datetime import date

from domain.members.entities import FitnessGoal
from domain.members.member import Member
from domain.members.value_objects import FitnessLevel, GoalType, Membership, MembershipTier
from domain.shared.value_objects import Email, FullName, PhoneNumber
from infrastructure.database.models.member_models import FitnessGoalORM, MemberORM


class MemberMapper:
    @staticmethod
    def to_domain(orm: MemberORM) -> Member:
        goals = [
            FitnessGoal(
                id=g.id,
                type=GoalType(g.type),
                description=g.description,
                target_date=g.target_date,
                achieved=g.achieved,
            )
            for g in (orm.goals or [])
        ]
        member = Member(
            id=orm.id,
            name=FullName(orm.first_name, orm.last_name),
            email=Email(orm.email),
            phone=PhoneNumber(orm.phone),
            fitness_level=FitnessLevel(orm.fitness_level),
            membership=Membership(
                tier=MembershipTier(orm.membership_tier),
                valid_until=orm.membership_valid_until,
            ),
            goals=goals,
            active_plan_id=orm.active_plan_id,
        )
        return member

    @staticmethod
    def to_orm(member: Member) -> MemberORM:
        orm = MemberORM(
            id=member.id,
            first_name=member.name.first_name,
            last_name=member.name.last_name,
            email=member.email.value,
            phone=member.phone.value,
            fitness_level=member.fitness_level.value,
            membership_tier=member.membership.tier.value,
            membership_valid_until=member.membership.valid_until,
            active_plan_id=member.active_plan_id,
            goals=[
                FitnessGoalORM(
                    id=g.id,
                    member_id=member.id or 0,
                    type=g.type.value,
                    description=g.description,
                    target_date=g.target_date,
                    achieved=g.achieved,
                )
                for g in member.goals
            ],
        )
        return orm
