from dataclasses import dataclass
from typing import Literal


@dataclass
class Sort:
    field: str
    direction: Literal["asc", "desc"] = "asc"
