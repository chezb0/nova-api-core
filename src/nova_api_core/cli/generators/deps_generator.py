from pathlib import Path

from nova_api_core.cli.generators.context.crud_context import CrudContext
from nova_api_core.core.types.database_type import DatabaseType

BASE_IMPORTS = """from functools import lru_cache
from nova_api_core.core.abstraction.logger import Logger
from nova_api_core.core.abstraction.database_manager import DatabaseManager
from fastapi import Request, Depends
"""


class DepsGenerator:

    def __init__(self, context: CrudContext):
        self.context = context

    def generate(self):
        self._ensure_directory()

        if self.context.db_type == DatabaseType.SQLALCHEMY:
            self._generate_sqlalchemy_deps()

        elif self.context.db_type == DatabaseType.MONGODB:
            self._generate_mongo_deps()

        else:
            raise Exception("Unsupported database type")

    # =========================
    # ENSURE DIRECTORY
    # =========================
    def _ensure_directory(self) -> None:
        """
        Ensure that the model directory exists before writing the file.
        """
        model_dir = Path(self.context.deps_file_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)

    def _generate_sqlalchemy_deps(self):

        name = self.context.name
        ClassName = name.capitalize()

        content = f"""{BASE_IMPORTS}

from nova_api_core.infra.db.sqlalchemy.sqlalchemy_generic_crud import SQLAlchemyGenericCRUD

from core.domain.models.{name} import {ClassName}

# =========================
# USE CASES
# =========================
from core.use_cases.{name}.get_all import Get{ClassName}UseCase
from core.use_cases.{name}.get_by_id import Get{ClassName}ByIdUseCase
from core.use_cases.{name}.create import Create{ClassName}UseCase
from core.use_cases.{name}.update import Update{ClassName}UseCase
from core.use_cases.{name}.delete import Delete{ClassName}UseCase
from core.use_cases.{name}.execute_sql import ExecuteSql{ClassName}UseCase

# =========================
# LOGGER
# =========================
def get_logger_dep(request: Request) -> Logger:
    return request.app.state.logger


# =========================
# Get session
# =========================
async def get_db_session(request: Request):
    async with request.app.state.db.get_session() as session:
        yield session

# =========================
# CRUD
# =========================
@lru_cache()
def get_{name}_crud():
    return SQLAlchemyGenericCRUD(model={ClassName})


# =========================
# GET ALL
# =========================
def get_{name}_use_case(logger: Logger = Depends(get_logger_dep)):
    return Get{ClassName}UseCase(
        crud=get_{name}_crud(),
        logger=logger,
    )


# =========================
# GET BY ID
# =========================
def get_{name}_by_id_use_case(logger: Logger = Depends(get_logger_dep)):
    return Get{ClassName}ByIdUseCase(
        crud=get_{name}_crud(),
        logger=logger,
    )


# =========================
# CREATE
# =========================
def create_{name}_use_case(logger: Logger = Depends(get_logger_dep)):
    return Create{ClassName}UseCase(
        crud=get_{name}_crud(),
        logger=logger,
    )


# =========================
# UPDATE
# =========================
def update_{name}_use_case(logger: Logger = Depends(get_logger_dep)):
    return Update{ClassName}UseCase(
        crud=get_{name}_crud(),
        logger=logger,
    )


# =========================
# DELETE
# =========================
def delete_{name}_use_case(logger: Logger = Depends(get_logger_dep)):
    return Delete{ClassName}UseCase(
        crud=get_{name}_crud(),
        logger=logger,
    )


# =========================
# RAW SQL
# =========================
def execute_sql_{name}_use_case(logger: Logger = Depends(get_logger_dep)):
    return ExecuteSql{ClassName}UseCase(
        crud=get_{name}_crud(),
        logger=logger,
    )
"""

        Path(self.context.deps_file_path).write_text(content)

    def _generate_mongo_deps(self):

        name = self.context.name
        ClassName = name.capitalize()

        content = f"""{BASE_IMPORTS}

from nova_api_core.infra.db.mongo.mongo_generic_crud import MongoGenericCRUD


# =========================
# LOGGER
# =========================
def get_logger_dep(request: Request) -> Logger:
    return request.app.state.logger


# =========================
# Get session
# =========================
async def get_db_session(request: Request):
    async with request.app.state.db.get_session() as session:
        yield session


# =========================
# CRUD
# =========================
@lru_cache()
def get_{name}_crud():
    return MongoGenericCRUD(collection_name="{name}")


# =========================
# USE CASES
# =========================
from core.use_cases.{name}.get_all import Get{ClassName}UseCase
from core.use_cases.{name}.get_by_id import Get{ClassName}ByIdUseCase
from core.use_cases.{name}.create import Create{ClassName}UseCase
from core.use_cases.{name}.update import Update{ClassName}UseCase
from core.use_cases.{name}.delete import Delete{ClassName}UseCase
from core.use_cases.{name}.find_raw import Find{ClassName}RawUseCase
from core.use_cases.{name}.aggregate_raw import Aggregate{ClassName}RawUseCase


# =========================
# GET ALL
# =========================
def get_{name}_use_case(logger: Logger = Depends(get_logger_dep)):
    return Get{ClassName}UseCase(
        crud=get_{name}_crud(),
        logger=logger,
    )


# =========================
# GET BY ID
# =========================
def get_{name}_by_id_use_case(logger: Logger = Depends(get_logger_dep)):
    return Get{ClassName}ByIdUseCase(
        crud=get_{name}_crud(),
        logger=logger,
    )


# =========================
# CREATE
# =========================
def create_{name}_use_case(logger: Logger = Depends(get_logger_dep)):
    return Create{ClassName}UseCase(
        crud=get_{name}_crud(),
        logger=logger,
    )


# =========================
# UPDATE
# =========================
def update_{name}_use_case(logger: Logger = Depends(get_logger_dep)):
    return Update{ClassName}UseCase(
        crud=get_{name}_crud(),
        logger=logger,
    )


# =========================
# DELETE
# =========================
def delete_{name}_use_case(logger: Logger = Depends(get_logger_dep)):
    return Delete{ClassName}UseCase(
        crud=get_{name}_crud(),
        logger=logger,
    )


# =========================
# RAW MONGO
# =========================
def find_raw_{name}_use_case(logger: Logger = Depends(get_logger_dep)):
    return Find{ClassName}RawUseCase(
        crud=get_{name}_crud(),
        logger=logger,
    )


def aggregate_raw_{name}_use_case(logger: Logger = Depends(get_logger_dep)):
    return Aggregate{ClassName}RawUseCase(
        crud=get_{name}_crud(),
        logger=logger,
    )
"""

        Path(self.context.deps_file_path).write_text(content)
