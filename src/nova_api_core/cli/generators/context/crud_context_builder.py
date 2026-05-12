from pathlib import Path

from nova_api_core.cli.context.config_loader import load_nova_config
from nova_api_core.core.types.database_type import DatabaseType
from .crud_context import CrudContext


class CrudContextBuilder:

    def __init__(self, name: str):
        self.name = name

    def build(self) -> CrudContext:

        config = load_nova_config()
        db_type = DatabaseType(config["database"])

        base_path = Path.cwd()

        name = self.name

        model_name = name.capitalize()

        id_type = "objectid" if db_type == DatabaseType.MONGODB else "int"

        return CrudContext(
            # =========================
            # BASIC INFO
            # =========================
            name=name,
            db_type=db_type,
            # =========================
            # NAMING
            # =========================
            model_name=model_name,
            schema_name=f"{model_name}Schema",
            domain_name=f"{model_name}Domain",
            # =========================
            # FILE PATHS
            # =========================
            model_path=str(base_path / f"core/domain/models/{name}.py"),
            schema_path=str(base_path / f"presentation/schemas/{name}"),
            domain_path=str(base_path / f"core/domain/entities/{name}.py"),
            route_file_path=str(base_path / f"presentation/routes/{name}/route.py"),
            deps_file_path=str(base_path / f"presentation/routes/{name}/deps.py"),
            # =========================
            # USE CASES
            # =========================
            get_all_use_case_name=f"Get{model_name}sUseCase",
            get_by_id_use_case_name=f"Get{model_name}ByIdUseCase",
            create_use_case_name=f"Create{model_name}UseCase",
            update_use_case_name=f"Update{model_name}UseCase",
            delete_use_case_name=f"Delete{model_name}UseCase",
            # =========================
            # STRATEGY
            # =========================
            id_type=id_type,
        )
