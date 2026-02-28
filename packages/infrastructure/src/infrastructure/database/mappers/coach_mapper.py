
from domain.coaches.coach import Coach
from domain.coaches.entities import AvailabilitySlot, Certification
from domain.coaches.value_objects import CoachTier, Specialization, Weekday
from domain.shared.value_objects import Email, FullName
from infrastructure.database.models.coach_models import (
    AvailabilitySlotORM,
    CertificationORM,
    CoachORM,
    CoachSpecializationORM,
)


class CoachMapper:
    @staticmethod
    def to_domain(orm: CoachORM) -> Coach:
        certs = [
            Certification(
                id=c.id,
                name=c.name,
                issuing_body=c.issuing_body,
                issued_at=c.issued_at,
                expires_at=c.expires_at,
            )
            for c in (orm.certifications or [])
        ]
        slots = [
            AvailabilitySlot(
                id=s.id,
                day=Weekday(s.day),
                start_hour=s.start_hour,
                end_hour=s.end_hour,
            )
            for s in (orm.available_slots or [])
        ]
        specs = frozenset(
            Specialization(row.specialization)
            for row in (orm.specializations or [])
        )
        return Coach(
            id=orm.id,
            name=FullName(first_name=orm.first_name, last_name=orm.last_name),
            email=Email(value=orm.email),
            bio=orm.bio,
            tier=CoachTier(orm.tier),
            specializations=specs,
            max_clients=orm.max_clients,
            current_client_count=orm.current_client_count,
            certifications=certs,
            available_slots=slots,
        )

    @staticmethod
    def to_orm(coach: Coach) -> CoachORM:
        cid = coach.id or 0
        certs = [
            CertificationORM(
                id=c.id,
                coach_id=cid,
                name=c.name,
                issuing_body=c.issuing_body,
                issued_at=c.issued_at,
                expires_at=c.expires_at,
            )
            for c in coach.certifications
        ]
        slots = [
            AvailabilitySlotORM(
                id=s.id,
                coach_id=cid,
                day=s.day.value,
                start_hour=s.start_hour,
                end_hour=s.end_hour,
            )
            for s in coach.available_slots
        ]
        spec_rows = [
            CoachSpecializationORM(coach_id=cid, specialization=spec.value)
            for spec in coach.specializations
        ]
        return CoachORM(
            id=coach.id,
            first_name=coach.name.first_name,
            last_name=coach.name.last_name,
            email=coach.email.value,
            bio=coach.bio,
            tier=coach.tier.value,
            max_clients=coach.max_clients,
            current_client_count=coach.current_client_count,
            certifications=certs,
            available_slots=slots,
            specializations=spec_rows,
        )
