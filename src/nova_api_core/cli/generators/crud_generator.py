from pathlib import Path

from nova_api_core.cli.context.config_loader import load_nova_config
from nova_api_core.core.types.database_type import DatabaseType


class CrudGenerator:

    def __init__(self, name: str):
        self.name = name
        self.config = load_nova_config()
        self.project_path = Path.cwd()

    # =========================
    # ENTRYPOINT
    # =========================
    def generate(self) -> None:

        db_type = DatabaseType(self.config["database"])

        if db_type == DatabaseType.SQLALCHEMY:
            self._generate_sqlalchemy_crud()

        elif db_type == DatabaseType.MONGODB:
            self._generate_mongo_crud()

        else:
            raise Exception("Unsupported database type")
