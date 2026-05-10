from typing import Any, Dict
from nova_api_core.cli.renderers.base import BaseRenderer


class DatabaseRenderer(BaseRenderer):
    def __init__(self):
        super().__init__("nova_api_core.cli.templates.database")

    def render(self, db_type: str, context: Dict[str, Any] = None) -> str:
        # Le nom du template correspond au DatabaseType (sqlalchemy, mongodb)
        return self._load_template(db_type)