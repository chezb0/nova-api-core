from typing import Any, Dict
from nova_api_core.cli.renderers.config import ConfigRenderer
from nova_api_core.cli.renderers.database import DatabaseRenderer
from nova_api_core.cli.metadata.db_metadata import BOOTSTRAP_DEFAULTS, DB_METADATA
from nova_api_core.cli.renderers.structure import StructureRenderer
from nova_api_core.core.types.database_type import DatabaseType

class NovaRenderer:
    def __init__(self):
        self.db = DatabaseRenderer()
        self.config = ConfigRenderer()
        self.structure = StructureRenderer()

    def render_app_entrypoint(self, db_type: DatabaseType) -> str:
        """Produit le contenu final du fichier app.py avec les corrections d'injection."""
        metadata = DB_METADATA.get(db_type, DB_METADATA[DatabaseType.NONE])
        
        # Gestion du bloc de setup
        if db_type == DatabaseType.NONE:
            # On définit une fonction qui retourne None pour garder la structure
            db_setup_code = "def get_database_manager(config: AppConfig): return None"
        else:
            # On s'assure de charger le fichier .py.tmpl
            db_setup_code = self.db.render(f"{db_type.value}")

        # Chargement du template app.py.tmpl
        app_template = self.db._load_template("../app/app")

        # Application des remplacements
        content = app_template.replace(
            "{{DATABASE_IMPORT}}", 
            metadata.get("manager_import", "")
        )
        content = content.replace(
            "{{DATABASE_SETUP}}", 
            db_setup_code
        )
        
        return content

    def render_app_config(self, db_type: DatabaseType) -> str:
        """Produit le contenu de core/config/app_config.py."""
        metadata = DB_METADATA.get(db_type, DB_METADATA[DatabaseType.NONE])
        # On passe les champs au ConfigRenderer qui gère le template {{FIELDS}}
        return self.config.render("app_config", {"fields": metadata["config_fields"]})

    def render_env_content(self, db_type: DatabaseType, is_dev: bool = True) -> str:
        """Produit le contenu des fichiers .env."""
        metadata = DB_METADATA.get(db_type, DB_METADATA[DatabaseType.NONE])
        env_vars = metadata.get("env_defaults", {})
        
        # On peut ajouter des variables globales ici si besoin
        if is_dev:
            env_vars["DEBUG"] = "true"
            
        return self.config.render_env(env_vars)
    
    def render_bootstrap_env(self, project_name: str) -> str:
        """Produit le contenu du fichier .env.base."""
        variables = BOOTSTRAP_DEFAULTS.copy()
        variables["APP_NAME"] = project_name
        
        return self.config.render_env(variables)
    
    def render_pyproject(self, project_name: str) -> str:
        """Produit le contenu du fichier pyproject.toml pour l'utilisateur final."""
        return f"""[project]
name = "{project_name}"
version = "0.1.0"
requires-python = ">=3.12"

dependencies = [
    "nova-api-core @ git+https://github.com/chezb0/nova-api-core.git@latest"
]
"""

    def render_structure(self, template_name: str, context: dict = None) -> str:
        return self.structure.render(template_name, context)