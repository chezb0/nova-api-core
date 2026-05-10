from typing import Any, Dict

from nova_api_core.cli.renderers.base import BaseRenderer


class ConfigRenderer(BaseRenderer):
    def __init__(self):
        super().__init__("nova_api_core.cli.templates.config")

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        content = self._load_template(template_name)

        # Gestion des champs de la dataclass
        fields = context.get("fields", {})
        if not fields:
            fields_str = "    pass"
        else:
            fields_str = "\n".join([f"    {k}: {v}" for k, v in fields.items()])

        return content.replace("{{FIELDS}}", fields_str)

    def render_env(self, env_vars: Dict[str, Any]) -> str:
        """Génère le contenu du fichier .env"""
        return "\n".join([f"{k}={v}" for k, v in env_vars.items()])
