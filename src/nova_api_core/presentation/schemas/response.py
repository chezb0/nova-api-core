from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):  # type: ignore[misc]
    """
    Standard API response wrapper.

    This is the single response contract used across the entire framework.
    """

    status_code: int
    message: Optional[str] = None
    content: Optional[T] = None


class PaginatedContent(BaseModel, Generic[T]):  # type: ignore[misc]
    total: int
    data: list[T]


default_error_responses = {
    400: {"model": APIResponse[None], "description": "Bad Request"},
    401: {"model": APIResponse[None], "description": "Unauthorized"},
    404: {"model": APIResponse[None], "description": "Not Found"},
    422: {"model": APIResponse[None], "description": "Validation Error"},
    500: {"model": APIResponse[None], "description": "Internal Server Error"},
}


class PaginatedResponseSchema(BaseModel, Generic[T]):  # type: ignore[misc]
    """
    Generic paginated response schema used in API layer.
    """

    model_config = ConfigDict(from_attributes=True)

    total: int
    data: List[T]
