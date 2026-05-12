from typing import Any, Optional, Type, TypeVar, cast

from sqlalchemy import Result, and_, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from nova_api_core.core.abstraction.sqlalchemy_repository import SQLAlchemyRepository
from nova_api_core.core.application.exception.base import AppException
from nova_api_core.core.application.exception.exception import (
    DatabaseException,
    NotFoundException,
)
from nova_api_core.core.domain.entities.database.filter import Filter
from nova_api_core.core.domain.entities.database.pagination import (
    PaginatedResult,
)
from nova_api_core.core.domain.entities.database.sort import Sort
from nova_api_core.core.domain.entities.database.sqlalchemy.query import (
    SQLAlchemyQueryBuilder,
)

ModelType = TypeVar("ModelType")


class SQLAlchemyGenericCRUD(SQLAlchemyRepository[ModelType]):

    def __init__(self, model: Type[ModelType]):
        self.model = model

    # =========================
    # GET
    # =========================
    async def get(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[Sort] = None,
        filters: Optional[list[Filter]] = None,
    ) -> PaginatedResult[ModelType]:

        try:

            stmt = select(self.model)

            count_stmt = select(func.count()).select_from(self.model)

            # =========================
            # FILTERS
            # =========================
            if filters:

                conditions = SQLAlchemyQueryBuilder.build_filters(
                    model=self.model,
                    filters=filters,
                )

                # Apply joins (deduplicate to avoid multiple joins)
                joined_models = set()
                for condition in conditions:
                    for join in condition.joins:
                        join_key = str(join)
                        if join_key not in joined_models:
                            stmt = stmt.join(join)
                            count_stmt = count_stmt.join(join)
                            joined_models.add(join_key)

                and_conditions = [
                    c.condition for c in conditions if c.db_operator == "AND"
                ]

                or_conditions = [
                    c.condition for c in conditions if c.db_operator == "OR"
                ]

                if and_conditions:
                    stmt = stmt.where(and_(*and_conditions))
                    count_stmt = count_stmt.where(and_(*and_conditions))

                if or_conditions:
                    stmt = stmt.where(or_(*or_conditions))
                    count_stmt = count_stmt.where(or_(*or_conditions))

            # =========================
            # SORT
            # =========================
            if sort:

                try:
                    column = getattr(
                        self.model,
                        sort.field,
                    )

                except AttributeError:
                    raise DatabaseException(
                        message="Le champ de tri est invalide",
                        technical_details=(f"Unknown sort field " f"'{sort.field}'"),
                    )

                if sort.direction == "desc":
                    stmt = stmt.order_by(column.desc())
                else:
                    stmt = stmt.order_by(column.asc())

            # =========================
            # PAGINATION
            # =========================
            stmt = stmt.offset(skip).limit(limit)

            # =========================
            # EXECUTE DATA QUERY
            # =========================
            result = await session.execute(stmt)

            data = list(result.scalars().all())

            # =========================
            # EXECUTE COUNT QUERY
            # =========================
            total_result = await session.execute(count_stmt)

            total = total_result.scalar_one()

            return PaginatedResult(
                total=total,
                data=data,
            )

        except DatabaseException:
            raise

        except Exception as e:
            raise DatabaseException(
                message="Impossible de récupérer les ressources",
                technical_details=str(e),
            )

    # =========================
    # GET BY ID
    # =========================
    async def get_by_id(
        self,
        session: AsyncSession,
        entity_id: Any,
    ) -> Optional[ModelType]:

        try:

            stmt = select(self.model).where(
                self.model.id == entity_id  # type: ignore[attr-defined]
            )

            result = await session.execute(stmt)

            return cast(Optional[ModelType], result.scalar_one_or_none())

        except Exception as e:
            raise DatabaseException(
                message="Impossible de récupérer la ressource",
                technical_details=str(e),
            )

    # =========================
    # CREATE
    # =========================
    async def create(
        self,
        session: AsyncSession,
        data: dict[str, Any],
    ) -> ModelType:

        try:

            entity = self.model(**data)

            session.add(entity)

            await session.flush()
            await session.refresh(entity)

            return entity

        except Exception as e:
            raise DatabaseException(
                message="Impossible de créer la ressource",
                technical_details=str(e),
            )

    # =========================
    # UPDATE
    # =========================
    async def update(
        self,
        session: AsyncSession,
        entity_id: Any,
        data: dict[str, Any],
    ) -> ModelType:

        try:
            entity = await self.get_by_id(session, entity_id)

            if not entity:
                raise NotFoundException(
                    message="Ressource introuvable",
                    technical_details=f"ID {entity_id} not found",
                )

            for key, value in data.items():
                setattr(entity, key, value)

            session.add(entity)

            await session.flush()
            await session.refresh(entity)

            return entity

        except AppException:
            raise

        except Exception as e:
            raise DatabaseException(
                message="Impossible de mettre à jour la ressource",
                technical_details=str(e),
            )

    # =========================
    # DELETE
    # =========================
    async def delete(
        self,
        session: AsyncSession,
        entity_id: Any,
    ) -> None:

        try:
            entity = await self.get_by_id(session, entity_id)

            if not entity:
                raise NotFoundException(
                    message="Ressource introuvable",
                    technical_details=f"ID {entity_id} not found",
                )

            await session.delete(entity)

        except AppException:
            raise

        except Exception as e:
            raise DatabaseException(
                message="Impossible de supprimer la ressource",
                technical_details=str(e),
            )

    # =========================
    # EXECUTE SQL
    # =========================
    async def execute_sql(
        self,
        session: AsyncSession,
        sql: str,
        params: Optional[dict[str, Any]] = None,
    ) -> Result[Any]:

        try:

            result = await session.execute(
                text(sql),
                params or {},
            )

            return result

        except Exception as e:
            raise DatabaseException(
                message="Impossible d'exécuter la requête SQL",
                technical_details=str(e),
            )
