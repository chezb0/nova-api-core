from typing import Protocol, Type

from nova_api_core.core.abstraction.logger import Logger
from nova_api_core.core.types.error import ErrorResponse


class ErrorHandler(Protocol):
    exception: Type[Exception]

    def handle(self, error: Exception, logger: Logger) -> "ErrorResponse": ...
