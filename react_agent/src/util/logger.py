"""Utility functions for logging"""

import logging

from react_agent.src.config.system_parameters import LoggerSettings

logger_settings = LoggerSettings()


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
        filename=logger_settings.filename,
        level=logger_settings.level,
        log_format=logger_settings.format,
    ):
        if not self._configured:
            logging.basicConfig(filename=filename, level=level, format=log_format)
            self._logger = logging.getLogger()
            self._configured = True

    @classmethod
    def get_logger(cls, name=None):
        instance = cls()
        if name:
            return logging.getLogger(name)
        return instance._logger
