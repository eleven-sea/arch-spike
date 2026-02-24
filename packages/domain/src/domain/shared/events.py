from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ApplicationEvent:
    """Base class for all domain events. Inherit all domain events from this."""
