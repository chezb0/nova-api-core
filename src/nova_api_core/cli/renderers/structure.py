from typing import Any, Dict
from nova_api_core.cli.renderers.base import BaseRenderer


class StructureRenderer(BaseRenderer):
    def __init__(self):
        # On cible directement le package 'structure' dans les templates
        super().__init__("nova_api_core.cli.templates.structure")

    def render(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """Charge le template et effectue les remplacements de variables."""
        # _load_template ira chercher dans ...templates.structure/
        content = self._load_template(template_name)
        
        if context:
            for key, value in context.items():
                content = content.replace(f"{{{{{key}}}}}", value)
        
        return content