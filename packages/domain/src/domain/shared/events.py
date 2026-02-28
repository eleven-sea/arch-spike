
from pydantic import BaseModel, ConfigDict


class ApplicationEvent(BaseModel):
    """Base class for all domain events. Inherit all domain events from this."""

    model_config = ConfigDict(frozen=True)
