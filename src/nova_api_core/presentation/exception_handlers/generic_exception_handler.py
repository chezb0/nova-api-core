from nova_api_core.core.abstraction.logger import Logger
from nova_api_core.core.types.error import ErrorResponse


class GenericExceptionHandler:
    exception = Exception

    def handle(self, error: Exception, logger: Logger) -> ErrorResponse:
        # Always log as ERROR (unexpected failure)
        logger.error(
            str(error) or "Unhandled exception",
            data={
                "type": error.__class__.__name__,
                "status_code": 500,
            },
        )

        # Return generic message (no internal details exposed)
        return ErrorResponse(
            status_code=500,
            message="Une erreur interne est survenue",
            data=None,
        )
