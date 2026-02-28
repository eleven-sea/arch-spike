
from enum import StrEnum

CoachId = int
CertId = int
SlotId = int


class CoachTier(StrEnum):
    STANDARD = "STANDARD"
    VIP = "VIP"


class Specialization(StrEnum):
    STRENGTH = "STRENGTH"
    CARDIO = "CARDIO"
    YOGA = "YOGA"
    CROSSFIT = "CROSSFIT"
    NUTRITION = "NUTRITION"


class Weekday(StrEnum):
    MON = "MON"
    TUE = "TUE"
    WED = "WED"
    THU = "THU"
    FRI = "FRI"
    SAT = "SAT"
    SUN = "SUN"
