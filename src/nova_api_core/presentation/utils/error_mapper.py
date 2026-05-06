from fastapi.responses import JSONResponse

from nova_api_core.core.types.error import ErrorResponse


def to_fastapi_response(err: ErrorResponse) -> JSONResponse:
    return JSONResponse(
        status_code=err.status_code,
        content={
            "message": err.message,
            "data": err.data,
        },
    )
