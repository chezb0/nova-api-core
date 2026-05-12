from typing import Any, Optional, Protocol, TypeVar

ModelType = TypeVar("ModelType", covariant=True)


class GenericRepository(Protocol[ModelType]):
    async def get_by_id(self, session: Any, entity_id: Any) -> Optional[ModelType]: ...

    async def get(
        self,
        session: Any,
        *,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[Any] = None,
        filters: Optional[list[Any]] = None,
    ) -> Any: ...

    async def create(self, session: Any, data: dict[str, Any]) -> ModelType: ...

    async def update(
        self, session: Any, entity_id: Any, data: dict[str, Any]
    ) -> ModelType: ...

    async def delete(self, session: Any, entity_id: Any) -> None: ...
