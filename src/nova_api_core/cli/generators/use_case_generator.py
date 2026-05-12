from pathlib import Path

from nova_api_core.cli.generators.context.crud_context import CrudContext
from nova_api_core.core.types.database_type import DatabaseType

BASE_IMPORTS_SQL = """
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from nova_api_core.core.abstraction.logger import Logger
from nova_api_core.core.abstraction.sqlalchemy_repository import SQLAlchemyRepository

from nova_api_core.core.domain.entities.database.sort import Sort
from nova_api_core.core.domain.entities.database.filter import Filter
"""

BASE_IMPORTS_MONGO = """
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from nova_api_core.core.abstraction.logger import Logger
from nova_api_core.core.abstraction.mongo_repository import MongoRepository

from nova_api_core.core.domain.entities.database.sort import Sort
from nova_api_core.core.domain.entities.database.filter import Filter
"""


class UseCaseGenerator:

    def __init__(self, context: CrudContext):
        self.context = context

    # =========================
    # ENTRYPOINT
    # =========================
    def generate(self) -> None:
        self._ensure_directory()
        self._generate_use_cases()

    # =========================
    # CREATE DIR
    # =========================
    def _ensure_directory(self):

        use_case_dir = Path(f"core/use_cases/{self.context.name}")
        use_case_dir.mkdir(parents=True, exist_ok=True)

    # =========================
    # GENERATE ALL USE CASES
    # =========================
    def _generate_use_cases(self):

        db_type = self.context.db_type

        # =========================
        # CRUD GENERATION
        # =========================
        if db_type == DatabaseType.SQLALCHEMY:
            self._generate_sqlalchemy_use_cases()

        elif db_type == DatabaseType.MONGODB:
            self._generate_mongo_use_cases()

        else:
            raise Exception("Unsupported database type")

    # =========================
    # GENERATE SQLALCHEMY USE CASES
    # =========================
    def _generate_sqlalchemy_use_cases(self):

        self._generate_sqlalchemy_get_all()
        self._generate_sqlalchemy_get_by_id()
        self._generate_sqlalchemy_create()
        self._generate_sqlalchemy_update()
        self._generate_sqlalchemy_delete()
        self._generate_sqlalchemy_execute_sql()

    def _generate_sqlalchemy_get_all(self):

        name = self.context.name

        content = f"""{BASE_IMPORTS_SQL}

class Get{name.capitalize()}UseCase:

    def __init__(self, crud: SQLAlchemyRepository, logger: Logger):
        self.crud = crud
        self.logger = logger

    async def execute(
        self,
        session,
        skip: int = 0,
        limit: int = 100,
        sort: Sort | None = None,
        filters: list[Filter] | None = None,
    ):

        self.logger.info("Get all {name}")

        return await self.crud.get(
            session=session,
            skip=skip,
            limit=limit,
            sort=sort,
            filters=filters,
        )
    """

        self._write(name, "get_all", content)

    def _generate_sqlalchemy_get_by_id(self):

        name = self.context.name

        content = f"""{BASE_IMPORTS_SQL}

class Get{name.capitalize()}ByIdUseCase:

    def __init__(self, crud: SQLAlchemyRepository, logger: Logger):
        self.crud = crud
        self.logger = logger

    async def execute(self, session, entity_id: Any):

        self.logger.info("Get {name} by id")

        return await self.crud.get_by_id(
            session=session,
            entity_id=entity_id,
        )
    """

        self._write(name, "get_by_id", content)

    def _generate_sqlalchemy_create(self):

        name = self.context.name

        content = f"""{BASE_IMPORTS_SQL}

class Create{name.capitalize()}UseCase:

    def __init__(self, crud: SQLAlchemyRepository, logger: Logger):
        self.crud = crud
        self.logger = logger

    async def execute(self, session, data: dict[str, Any]):

        self.logger.info("Create {name}")

        return await self.crud.create(
            session=session,
            data=data,
        )
    """

        self._write(name, "create", content)

    def _generate_sqlalchemy_update(self):

        name = self.context.name

        content = f"""{BASE_IMPORTS_SQL}

class Update{name.capitalize()}UseCase:

    def __init__(self, crud: SQLAlchemyRepository, logger: Logger):
        self.crud = crud
        self.logger = logger

    async def execute(self, session, entity_id: Any, data: dict[str, Any]):

        self.logger.info("Update {name}")

        return await self.crud.update(
            session=session,
            entity_id=entity_id,
            data=data,
        )
    """

        self._write(name, "update", content)

    def _generate_sqlalchemy_delete(self):

        name = self.context.name

        content = f"""{BASE_IMPORTS_SQL}

class Delete{name.capitalize()}UseCase:

    def __init__(self, crud: SQLAlchemyRepository, logger: Logger):
        self.crud = crud
        self.logger = logger

    async def execute(self, session, entity_id: Any):

        self.logger.info("Delete {name}")

        return await self.crud.delete(
            session=session,
            entity_id=entity_id,
        )
    """

        self._write(name, "delete", content)

    def _generate_sqlalchemy_execute_sql(self):

        name = self.context.name

        content = f"""{BASE_IMPORTS_SQL}


class ExecuteSql{name.capitalize()}UseCase:

    def __init__(self, crud: SQLAlchemyRepository, logger: Logger):
        self.crud = crud
        self.logger = logger

    async def execute(
        self,
        session: AsyncSession,
        sql: str,
        params: Optional[dict[str, Any]] = None,
    ) -> Any:

        self.logger.info("Executing raw SQL for {name}")

        return await self.crud.execute_sql(
            session=session,
            sql=sql,
            params=params,
        )
    """

        self._write(name, "execute_sql", content)

    def _generate_mongo_use_cases(self):

        self._generate_mongo_get_all()
        self._generate_mongo_get_by_id()
        self._generate_mongo_create()
        self._generate_mongo_update()
        self._generate_mongo_delete()

        # RAW METHODS (spécifiques Mongo)
        self._generate_mongo_find_raw()
        self._generate_mongo_aggregate_raw()

    def _generate_mongo_get_all(self):

        name = self.context.name

        content = f"""{BASE_IMPORTS_MONGO}

class Get{name.capitalize()}UseCase:

    def __init__(self, crud: MongoRepository, logger: Logger):
        self.crud = crud
        self.logger = logger

    async def execute(
        self,
        session: AsyncIOMotorDatabase,
        skip: int = 0,
        limit: int = 100,
        sort: Sort | None = None,
        filters: list[Filter] | None = None,
    ):

        self.logger.info("Get all {name}")

        return await self.crud.get(
            session=session,
            skip=skip,
            limit=limit,
            sort=sort,
            filters=filters,
        )
    """

        self._write(name, "get_all", content)

    def _generate_mongo_get_by_id(self):

        name = self.context.name

        content = f"""{BASE_IMPORTS_MONGO}

class Get{name.capitalize()}ByIdUseCase:

    def __init__(self, crud: MongoRepository, logger: Logger):
        self.crud = crud
        self.logger = logger

    async def execute(self, session: AsyncIOMotorDatabase, entity_id: Any):

        self.logger.info("Get {name} by id")

        return await self.crud.get_by_id(
            session=session,
            entity_id=entity_id,
        )
    """

        self._write(name, "get_by_id", content)

    def _generate_mongo_create(self):

        name = self.context.name

        content = f"""{BASE_IMPORTS_MONGO}

class Create{name.capitalize()}UseCase:

    def __init__(self, crud: MongoRepository, logger: Logger):
        self.crud = crud
        self.logger = logger

    async def execute(self, session: AsyncIOMotorDatabase, data: dict[str, Any]):

        self.logger.info("Create {name}")

        return await self.crud.create(
            session=session,
            data=data,
        )
    """

        self._write(name, "create", content)

    def _generate_mongo_update(self):

        name = self.context.name

        content = f"""{BASE_IMPORTS_MONGO}

class Update{name.capitalize()}UseCase:

    def __init__(self, crud: MongoRepository, logger: Logger):
        self.crud = crud
        self.logger = logger

    async def execute(
        self,
        session: AsyncIOMotorDatabase,
        entity_id: Any,
        data: dict[str, Any],
    ):

        self.logger.info("Update {name}")

        return await self.crud.update(
            session=session,
            entity_id=entity_id,
            data=data,
        )
    """

        self._write(name, "update", content)

    def _generate_mongo_delete(self):

        name = self.context.name

        content = f"""{BASE_IMPORTS_MONGO}

class Delete{name.capitalize()}UseCase:

    def __init__(self, crud: MongoRepository, logger: Logger):
        self.crud = crud
        self.logger = logger

    async def execute(self, session: AsyncIOMotorDatabase, entity_id: Any):

        self.logger.info("Delete {name}")

        return await self.crud.delete(
            session=session,
            entity_id=entity_id,
        )
    """

        self._write(name, "delete", content)

    def _generate_mongo_find_raw(self):

        name = self.context.name

        content = f"""{BASE_IMPORTS_MONGO}

class Find{name.capitalize()}RawUseCase:

    def __init__(self, crud: MongoRepository, logger: Logger):
        self.crud = crud
        self.logger = logger

    async def execute(
        self,
        session: AsyncIOMotorDatabase,
        query: dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        sort: list[tuple[str, int]] | None = None,
    ):

        self.logger.info("Find raw {name}")

        return await self.crud.find_raw(
            session=session,
            query=query,
            skip=skip,
            limit=limit,
            sort=sort,
        )
    """

        self._write(name, "find_raw", content)

    def _generate_mongo_aggregate_raw(self):

        name = self.context.name

        content = f"""{BASE_IMPORTS_MONGO}

class Aggregate{name.capitalize()}RawUseCase:

    def __init__(self, crud: MongoRepository, logger: Logger):
        self.crud = crud
        self.logger = logger

    async def execute(
        self,
        session: AsyncIOMotorDatabase,
        pipeline: list[dict[str, Any]],
    ):

        self.logger.info("Aggregate {name}")

        return await self.crud.aggregate_raw(
            session=session,
            pipeline=pipeline,
        )
    """

        self._write(name, "aggregate_raw", content)

    def _write(self, name: str, filename: str, content: str):
        Path(f"core/use_cases/{name}/{filename}.py").write_text(content)
