import importlib.resources as pkg_resources
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseRenderer(ABC):
    def __init__(self, template_package: str):
        self.template_package = template_package

    def _load_template(self, template_name: str) -> str:
        """Lit le fichier .tmpl brut."""
        source = pkg_resources.files(self.template_package).joinpath(
            f"{template_name}.py.tmpl"
        )
        return source.read_text()

    @abstractmethod
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        pass
