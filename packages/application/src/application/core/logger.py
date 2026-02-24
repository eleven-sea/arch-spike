import logging
from typing import Protocol


class ILogger(Protocol):
    def get_logger(self, name: str) -> logging.Logger: ...
