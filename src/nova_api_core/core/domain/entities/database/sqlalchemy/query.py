from dataclasses import dataclass, field
from typing import Any

from nova_api_core.core.application.exception.exception import (
    DatabaseException,
)
from nova_api_core.core.domain.entities.database.filter import Filter


@dataclass
class QueryCondition:
    db_operator: str
    condition: Any
    joins: list[Any] = field(default_factory=list)


class SQLAlchemyQueryBuilder:

    # =========================
    # BUILD FILTER CONDITIONS
    # =========================
    @staticmethod
    def build_filters(
        *,
        model: Any,
        filters: list[Filter],
    ) -> list[QueryCondition]:

        conditions: list[QueryCondition] = []

        for filter_item in filters:

            column, joins = SQLAlchemyQueryBuilder._resolve_nested_field(
                model=model,
                field_path=filter_item.field,
            )

            condition = SQLAlchemyQueryBuilder._build_operator_condition(
                column=column,
                operator=filter_item.operator,
                value=filter_item.value,
            )

            conditions.append(
                QueryCondition(
                    db_operator=filter_item.db_operator,
                    condition=condition,
                    joins=joins,
                )
            )

        return conditions

    # =========================
    # RESOLVE NESTED FIELDS
    # =========================
    @staticmethod
    def _resolve_nested_field(
        *,
        model: Any,
        field_path: str,
    ) -> tuple[Any, list[Any]]:
        """
        Resolve nested field paths (e.g., 'products.provider.name').
        Returns the final column and list of relationships to join.
        """
        parts = field_path.split(".")

        if len(parts) == 1:
            try:
                column = getattr(model, field_path)
                return column, []
            except AttributeError:
                raise DatabaseException(
                    message="Invalid filter requested",
                    technical_details=(
                        f"Unknown field '{field_path}' " f"for model '{model.__name__}'"
                    ),
                )

        joins = []
        current_model = model
        current_attr = None

        for i, part in enumerate(parts[:-1]):
            try:
                current_attr = getattr(current_model, part)
            except AttributeError:
                raise DatabaseException(
                    message="Invalid filter requested",
                    technical_details=(
                        f"Unknown relationship '{part}' "
                        f"for model '{current_model.__name__}'"
                    ),
                )

            try:
                mapper = current_attr.property.mapper
                current_model = mapper.class_
                joins.append(current_attr)
            except (AttributeError, ValueError):
                raise DatabaseException(
                    message="Invalid filter requested",
                    technical_details=(
                        f"'{part}' is not a valid relationship "
                        f"for model '{current_model.__name__}'"
                    ),
                )

        try:
            final_column = getattr(current_model, parts[-1])
        except AttributeError:
            raise DatabaseException(
                message="Invalid filter requested",
                technical_details=(
                    f"Unknown field '{parts[-1]}' "
                    f"for model '{current_model.__name__}'"
                ),
            )

        return final_column, joins

    # =========================
    # BUILD OPERATOR CONDITION
    # =========================
    @staticmethod
    def _build_operator_condition(
        *,
        column: Any,
        operator: str,
        value: Any,
    ) -> Any:

        if operator == "equals":
            return column == value
        elif operator == "not_equals":
            return column != value
        elif operator == "like":
            return column.like(f"%{value}%")
        elif operator == "ilike":
            return column.ilike(f"%{value}%")
        elif operator == "gt":
            return column > value
        elif operator == "gte":
            return column >= value
        elif operator == "lt":
            return column < value
        elif operator == "lte":
            return column <= value
        elif operator == "in":
            return column.in_(value)
        else:
            raise DatabaseException(
                message="Invalid filter operator",
                technical_details=f"Unsupported operator '{operator}'",
            )
