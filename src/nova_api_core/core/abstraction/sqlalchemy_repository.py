from typing import Optional, Any, TypeVar

from nova_api_core.core.abstraction.generic_repository import GenericRepository

ModelType = TypeVar("ModelType", covariant=True)


class SQLAlchemyRepository(GenericRepository[ModelType]):

    # =========================
    # RAW SQL EXECUTION
    # =========================
    async def execute_sql(
        self,
        session: Any,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> Any: ...
