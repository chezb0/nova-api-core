from nova_api_core.core.abstraction.logger import Logger
from nova_api_core.core.application.exception.base import AppException
from nova_api_core.core.types.error import ErrorResponse


class AppExceptionHandler:
    exception = AppException

    def handle(self, error: AppException, logger: Logger) -> ErrorResponse:
        # Determine log level based on HTTP status code
        if error.status_code >= 500:
            log_method = logger.error
        else:
            log_method = logger.warning

        # Log only technical details (not user-facing message)
        log_method(
            error.technical_details or "No technical details provided",
            data={
                "type": error.__class__.__name__,
                "status_code": error.status_code,
            },
        )

        # Return clean response to client
        return ErrorResponse(
            status_code=error.status_code,
            message=error.message,
            data=None,
        )
