import logging
import sys
from typing import Any, Optional

from nova_api_core.core.application.exception.exception import ConfigurationException
from nova_api_core.infra.logger.base import JsonFormatter


class JsonLogger:
    def __init__(
        self,
        *,
        app_name: str,
        environment: str,
        log_level: str = "DEBUG",
        log_output: str = "CONSOLE",
        log_file_path: Optional[str] = None,
    ) -> None:
        self._logger = logging.getLogger(app_name)
        self._logger.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))
        self._logger.propagate = False

        if self._logger.hasHandlers():
            self._logger.handlers.clear()

        formatter = JsonFormatter(app_name, environment)

        handler: logging.Handler

        if log_output == "FILE":
            if not log_file_path:
                raise ConfigurationException(
                    message="Configuration invalide du logger",
                    technical_details="log_file_path is required when log_output='FILE'",
                )
            handler = logging.FileHandler(log_file_path)
        else:
            handler = logging.StreamHandler(sys.stdout)

        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def _log(self, level: int, msg: str, data: Optional[Any] = None) -> None:
        extra = {"data": data} if data is not None else {}
        self._logger.log(level, msg, extra=extra)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(logging.INFO, msg, kwargs.get("data"))

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(logging.ERROR, msg, kwargs.get("data"))

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(logging.CRITICAL, msg, kwargs.get("data"))

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(logging.WARNING, msg, kwargs.get("data"))

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(logging.DEBUG, msg, kwargs.get("data"))
