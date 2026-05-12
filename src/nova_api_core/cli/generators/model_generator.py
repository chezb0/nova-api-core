from pathlib import Path

from nova_api_core.cli.generators.context.crud_context import CrudContext
from nova_api_core.core.types.database_type import DatabaseType


class ModelGenerator:

    def __init__(self, context: CrudContext):
        self.context = context

    def generate(self):
        self._ensure_directory()

        if self.context.db_type == DatabaseType.SQLALCHEMY:
            self._generate_sqlalchemy_model()

        elif self.context.db_type == DatabaseType.MONGODB:
            self._generate_mongo_model()

        else:
            raise Exception("Unsupported database type")

    # =========================
    # ENSURE DIRECTORY
    # =========================
    def _ensure_directory(self) -> None:
        """
        Ensure that the model directory exists before writing the file.
        """
        model_dir = Path(self.context.model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)

    def _generate_sqlalchemy_model(self):

        name = self.context.name
        class_name = name.capitalize()

        content = f'''
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class {class_name}(Base):
    """
    SQLAlchemy model.

    IMPORTANT:
    - Define your business fields here
    - Do not remove the id field
    """

    __tablename__ = "{name}"

    id = Column(String, primary_key=True, index=True)

    # =========================
    # ADD YOUR FIELDS HERE
    # =========================
    # name = Column(String)
    # email = Column(String, unique=True)
    '''

        Path(self.context.model_path).write_text(content)

    def _generate_mongo_model(self):

        name = self.context.name
        class_name = name.capitalize()

        content = f'''"""
MongoDB model placeholder.

IMPORTANT:
- MongoDB does NOT require ORM models.
- This class is only a schema contract for developers.
"""

class {class_name}:
    """
    Mongo document structure.

    _id is automatically managed by MongoDB.

    Define your fields below.
    """

    # =========================
    # MONGODB FIELDS
    # =========================
    # name: str
    # email: str
    # age: int
    '''

        Path(self.context.model_path).write_text(content)
