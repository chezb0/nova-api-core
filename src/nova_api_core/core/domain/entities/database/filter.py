from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class Filter:
    field: str

    operator: Literal[
        "equals",
        "not_equals",
        "like",
        "ilike",
        "in",
        "gt",
        "gte",
        "lt",
        "lte",
    ]

    value: Any

    db_operator: Literal[
        "AND",
        "OR",
    ] = "AND"
