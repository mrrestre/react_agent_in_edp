import logging
import os
from pathlib import Path

from react_agent.src.config.system_parameters import LoggerSettings

LOGGER_SETTINGS = LoggerSettings()


class LoggerSingleton:
    """Singleton logger per process, with named logger support"""

    _configured_loggers = {}
    _filename = LOGGER_SETTINGS.filename
    _level = LOGGER_SETTINGS.level
    _log_format = LOGGER_SETTINGS.format

    @staticmethod
    def get_project_root() -> Path:
        """Returns the project root directory."""
        return Path(__file__).resolve().parents[3]

    @classmethod
    def get_logger(cls, name: str = None) -> logging.Logger:
        """Returns a named logger, configured only once per process."""
        logger_name = name or "react_agent_logger"

        if logger_name in cls._configured_loggers:
            return cls._configured_loggers[logger_name]

        abs_filename = os.path.join(cls.get_project_root(), cls._filename)
        os.makedirs(os.path.dirname(abs_filename), exist_ok=True)

        logger = logging.getLogger(logger_name)
        logger.setLevel(cls._level)

        if not logger.handlers:
            file_handler = logging.FileHandler(abs_filename)
            file_handler.setLevel(cls._level)
            formatter = logging.Formatter(cls._log_format)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.propagate = False

        cls._configured_loggers[logger_name] = logger
        return logger
