from typing import Protocol, Any, TypeVar

from nova_api_core.core.abstraction.generic_repository import GenericRepository

ModelType = TypeVar("ModelType")


class MongoRepository(GenericRepository[ModelType], Protocol):

    # =========================
    # RAW FIND
    # =========================
    async def find_raw(
        self,
        session: Any,
        query: dict[str, Any],
    ) -> list[ModelType]: ...

    # =========================
    # AGGREGATE PIPELINE
    # =========================
    async def aggregate_raw(
        self,
        session: Any,
        pipeline: list[dict[str, Any]],
    ) -> list[dict[str, Any]]: ...
