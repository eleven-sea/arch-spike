from __future__ import annotations

from enum import Enum

CoachId = int
CertId = int
SlotId = int


class CoachTier(str, Enum):
    STANDARD = "STANDARD"
    VIP = "VIP"


class Specialization(str, Enum):
    STRENGTH = "STRENGTH"
    CARDIO = "CARDIO"
    YOGA = "YOGA"
    CROSSFIT = "CROSSFIT"
    NUTRITION = "NUTRITION"


class Weekday(str, Enum):
    MON = "MON"
    TUE = "TUE"
    WED = "WED"
    THU = "THU"
    FRI = "FRI"
    SAT = "SAT"
    SUN = "SUN"
