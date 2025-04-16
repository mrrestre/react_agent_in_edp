"""Utility functions for logging"""

import logging
import os
from pathlib import Path

from react_agent.src.config.system_parameters import LoggerSettings

LOGGER_SETTINGS = LoggerSettings()


class LoggerSingleton:
    """Singleton class for logging"""

    _instance = None
    _logger = None
    _configured = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LoggerSingleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(
        self,
        filename=LOGGER_SETTINGS.filename,
        level=LOGGER_SETTINGS.level,
        log_format=LOGGER_SETTINGS.format,
    ):
        if not self._configured:
            abs_filename = os.path.join(LoggerSingleton.get_project_root(), filename)
            logging.basicConfig(filename=abs_filename, level=level, format=log_format)
            self._logger = logging.getLogger()
            self._configured = True

    @staticmethod
    def get_project_root() -> Path:
        """Returns the project root directory."""
        return Path(__file__).parent.parent.parent.parent

    @classmethod
    def get_logger(cls, name=None):
        """Returns the logger instance."""
        instance = cls()
        if name:
            return logging.getLogger(name)
        return instance._logger
