from typing import Any, Optional, TypeVar, cast

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from nova_api_core.core.abstraction.mongo_repository import MongoRepository
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

ModelType = TypeVar("ModelType")


class MongoGenericCRUD(MongoRepository[ModelType]):
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    # =========================
    # FILTER BUILDER
    # =========================
    def _build_mongo_filter(self, filters: list[Filter]) -> dict[str, Any]:
        query: dict[str, Any] = {}
        or_conditions: list[dict[str, Any]] = []

        for filter_item in filters:
            condition = self._build_mongo_condition(
                field=filter_item.field,
                operator=filter_item.operator,
                value=filter_item.value,
            )

            if filter_item.db_operator == "OR":
                or_conditions.append(condition)
            else:
                query.update(condition)

        if or_conditions:
            query["$or"] = or_conditions

        return query

    @staticmethod
    def _build_mongo_condition(
        field: str,
        operator: str,
        value: Any,
    ) -> dict[str, Any]:

        if operator == "equals":
            return {field: value}
        elif operator == "not_equals":
            return {field: {"$ne": value}}
        elif operator in ("like", "ilike"):
            return {field: {"$regex": value, "$options": "i"}}
        elif operator == "gt":
            return {field: {"$gt": value}}
        elif operator == "gte":
            return {field: {"$gte": value}}
        elif operator == "lt":
            return {field: {"$lt": value}}
        elif operator == "lte":
            return {field: {"$lte": value}}
        elif operator == "in":
            return {field: {"$in": value}}
        else:
            raise DatabaseException(
                message="L'opérateur de filtre est invalide",
                technical_details=f"Unsupported operator '{operator}'",
            )

    # =========================
    # GET LIST
    # =========================
    async def get(
        self,
        session: AsyncIOMotorDatabase,
        *,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[Sort] = None,
        filters: Optional[list[Filter]] = None,
    ) -> PaginatedResult[ModelType]:

        try:
            collection = session[self.collection_name]

            query: dict[str, Any] = {}

            if filters:
                query = self._build_mongo_filter(filters)

            total = await collection.count_documents(query)

            cursor = collection.find(query)

            if sort:
                direction = 1 if sort.direction == "asc" else -1
                cursor = cursor.sort(sort.field, direction)

            cursor = cursor.skip(skip).limit(limit)

            data = await cursor.to_list(length=limit)

            return PaginatedResult(
                total=total,
                data=cast(list[ModelType], data),
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
        session: AsyncIOMotorDatabase,
        entity_id: Any,
    ) -> Optional[ModelType]:

        try:
            collection = session[self.collection_name]

            if isinstance(entity_id, str):
                try:
                    entity_id = ObjectId(entity_id)
                except Exception:
                    return None

            result = await collection.find_one({"_id": entity_id})

            return cast(Optional[ModelType], result)

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
        session: AsyncIOMotorDatabase,
        data: dict[str, Any],
    ) -> ModelType:

        try:
            collection = session[self.collection_name]

            result = await collection.insert_one(data)

            created_document = await collection.find_one({"_id": result.inserted_id})

            if created_document is None:
                raise DatabaseException(
                    message="Erreur lors de la création de la ressource",
                    technical_details="Document not found after insert",
                )

            return cast(ModelType, created_document)

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
        session: AsyncIOMotorDatabase,
        entity_id: Any,
        data: dict[str, Any],
    ) -> ModelType:

        try:
            collection = session[self.collection_name]

            if isinstance(entity_id, str):
                try:
                    entity_id = ObjectId(entity_id)
                except Exception:
                    raise NotFoundException(
                        message="Ressource introuvable",
                        technical_details=f"ID {entity_id} not valid",
                    )

            result = await collection.update_one(
                {"_id": entity_id},
                {"$set": data},
            )

            if result.matched_count == 0:
                raise NotFoundException(
                    message="Ressource introuvable",
                    technical_details=f"ID {entity_id} not found",
                )

            updated_document = await collection.find_one({"_id": entity_id})

            if updated_document is None:
                raise DatabaseException(
                    message="Erreur lors de la mise à jour",
                    technical_details="Document not found after update",
                )

            return cast(ModelType, updated_document)

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
        session: AsyncIOMotorDatabase,
        entity_id: Any,
    ) -> None:

        try:
            collection = session[self.collection_name]

            if isinstance(entity_id, str):
                try:
                    entity_id = ObjectId(entity_id)
                except Exception:
                    raise NotFoundException(
                        message="Ressource introuvable",
                        technical_details=f"ID {entity_id} not valid",
                    )

            result = await collection.delete_one({"_id": entity_id})

            if result.deleted_count == 0:
                raise NotFoundException(
                    message="Ressource introuvable",
                    technical_details=f"ID {entity_id} not found",
                )

        except AppException:
            raise

        except Exception as e:
            raise DatabaseException(
                message="Impossible de supprimer la ressource",
                technical_details=str(e),
            )

    # =========================
    # FIND RAW
    # =========================
    async def find_raw(
        self,
        session: AsyncIOMotorDatabase,
        query: dict[str, Any],
        *,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[list[tuple[str, int]]] = None,
    ) -> list[ModelType]:

        try:
            collection = session[self.collection_name]

            cursor = collection.find(query)

            if sort:
                cursor = cursor.sort(sort)

            cursor = cursor.skip(skip).limit(limit)

            data = await cursor.to_list(length=limit)

            return cast(list[ModelType], data)

        except Exception as e:
            raise DatabaseException(
                message="Impossible d'exécuter la requête MongoDB",
                technical_details=str(e),
            )

    # =========================
    # AGGREGATE RAW
    # =========================
    async def aggregate_raw(
        self,
        session: AsyncIOMotorDatabase,
        pipeline: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        try:
            collection = session[self.collection_name]

            cursor = collection.aggregate(pipeline)

            result = await cursor.to_list(length=None)

            return cast(list[dict[str, Any]], result)

        except Exception as e:
            raise DatabaseException(
                message="Impossible d'exécuter le pipeline MongoDB",
                technical_details=str(e),
            )
