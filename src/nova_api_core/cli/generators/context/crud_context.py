from dataclasses import dataclass
from typing import Literal

from nova_api_core.core.types.database_type import DatabaseType


@dataclass
class CrudContext:
    name: str
    db_type: DatabaseType

    # naming helpers
    model_name: str
    schema_name: str
    domain_name: str

    # paths
    model_path: str
    schema_path: str
    domain_path: str

    route_file_path: str
    deps_file_path: str

    # use cases
    get_all_use_case_name: str
    get_by_id_use_case_name: str
    create_use_case_name: str
    update_use_case_name: str
    delete_use_case_name: str

    # strategy
    id_type: Literal["int", "objectid"]
