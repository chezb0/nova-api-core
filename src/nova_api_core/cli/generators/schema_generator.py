from pathlib import Path

from nova_api_core.cli.generators.context.crud_context import CrudContext

BASE_IMPORTS = """
from pydantic import BaseModel
from typing import Optional
"""


class SchemaGenerator:

    def __init__(self, context: CrudContext):
        self.context = context

    def generate(self):
        self._ensure_directory()

        self._generate_create_schema()
        self._generate_update_schema()
        self._generate_response_schema()

    # =========================
    # ENSURE DIRECTORY
    # =========================
    def _ensure_directory(self) -> None:
        """
        Ensure that the schema directory exists before writing the file.
        """
        schema_dir = Path(self.context.schema_path)
        schema_dir.mkdir(parents=True, exist_ok=True)

    def _generate_create_schema(self):

        name = self.context.name
        class_name = name.capitalize()

        content = f'''{BASE_IMPORTS}

class Create{class_name}Schema(BaseModel):
    """
    Schema used for creating a {name}.

    This represents the full input contract accepted by the API.
    """

    # =========================
    # REQUIRED FIELDS
    # =========================
    # name: str
    # email: str

    # =========================
    # OPTIONAL FIELDS
    # =========================
    # is_active: Optional[bool] = True
    # metadata: Optional[dict] = None
    '''
        self._write("create", content)

    def _generate_update_schema(self):

        name = self.context.name
        class_name = name.capitalize()

        content = f'''{BASE_IMPORTS}

class Update{class_name}Schema(BaseModel):
    """
    Schema used for updating a {name}.

    All fields are optional.
    """

    # =========================
    # OPTIONAL FIELDS
    # =========================
    # name: Optional[str] = None
    # email: Optional[str] = None
    '''
        self._write("update", content)

    def _generate_response_schema(self):

        name = self.context.name
        class_name = name.capitalize()

        content = f'''{BASE_IMPORTS}

class {class_name}Schema(BaseModel):
    """
    Response schema for {name}.

    This represents what is returned by the API.
    """

    id: str

    # =========================
    # RESPONSE FIELDS
    # =========================
    # name: str
    # email: str
    '''
        self._write("response", content)

    def _write(self, filename: str, content: str):
        schema_file = Path(self.context.schema_path) / f"{filename}.py"
        schema_file.write_text(content)
