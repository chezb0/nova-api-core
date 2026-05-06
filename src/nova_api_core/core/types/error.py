from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class ErrorResponse:
    status_code: int
    message: str
    data: Optional[Any] = None
