import json
import logging
import traceback
from datetime import datetime, timezone

from nova_api_core.core.abstraction.logger import Logger


class JsonFormatter(logging.Formatter):
    def __init__(self, app_name: str, environment: str):
        super().__init__()
        self.app_name = app_name
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "environment": self.environment,
            "app_name": self.app_name,
        }

        # Inject structured data if present
        if hasattr(record, "data"):
            log["data"] = record.data

        return json.dumps(log, default=str)


def setup_uvicorn_logging(logger: Logger, log_level: str) -> None:

    level = getattr(logging, log_level.upper(), logging.INFO)

    level_map = {
        logging.DEBUG: logger.debug,
        logging.INFO: logger.info,
        logging.WARNING: logger.warning,
        logging.ERROR: logger.error,
        logging.CRITICAL: logger.critical,
    }

    class InterceptHandler(logging.Handler):

        def emit(self, record: logging.LogRecord) -> None:
            try:

                if (
                    record.name == "uvicorn.error"
                    and record.exc_info
                ):
                    return

                message = record.getMessage()

                if message.startswith("Traceback (most recent call last):"):
                    return

                log_func = level_map.get(record.levelno, logger.info)

                log_func(
                    message,
                    data={
                        "logger": record.name,
                        "level": record.levelname,
                    },
                )

            except Exception:
                pass

    logging.basicConfig(
        handlers=[InterceptHandler()],
        level=level,
    )

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "starlette"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers = [InterceptHandler()]
        uv_logger.setLevel(level)
        uv_logger.propagate = False
