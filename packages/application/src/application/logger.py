import logging
import sys
from typing import override

from application.core.logger import ILogger


class ApplicationLogger(ILogger):
    def __init__(self, level: int = logging.DEBUG) -> None:
        self._level = level
        self._setup()

    def _setup(self) -> None:
        root = logging.getLogger()
        root.setLevel(self._level)

        if not root.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(self._level)
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            root.addHandler(handler)

    @override
    def get_logger(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(self._level)
        return logger
