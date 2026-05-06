from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class LimitOffset:
    skip: int = 0
    limit: int = 20


SortDirection = Literal["asc", "desc"]


@dataclass(frozen=True)
class Sort:
    field: str
    direction: SortDirection = "asc"
