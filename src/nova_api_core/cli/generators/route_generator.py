from pathlib import Path
from nova_api_core.cli.generators.context.crud_context import CrudContext


class RouteGenerator:

    def __init__(self, context: CrudContext):
        self.context = context

    # =========================
    # ENTRYPOINT
    # =========================
    def generate(self) -> None:
        self._ensure_directory()
        self._generate_route_file()
        self._generate_init_file()
        self._update_global_routes_init()

    # =========================
    # ENSURE DIRECTORY
    # =========================
    def _ensure_directory(self):
        route_dir = Path(self.context.route_file_path).parent
        route_dir.mkdir(parents=True, exist_ok=True)

    # =========================
    # UPDATE GLOBAL ROUTES INIT
    # =========================
    def _update_global_routes_init(self):
        """Add the new router to the global ROUTES list in presentation/routes/__init__.py"""
        name = self.context.name
        routes_init_path = Path("presentation/routes/__init__.py")

        if not routes_init_path.exists():
            return

        content = routes_init_path.read_text()

        import_line = f"from .{name} import router as {name}_router\n"
        routes_entry = f"    {name}_router,\n"

        if f"{name}_router" in content:
            return

        lines = content.split("\n")
        new_lines = []
        routes_index = -1

        for i, line in enumerate(lines):
            if line.startswith("ROUTES = "):
                routes_index = i
                break
            new_lines.append(line)

        if routes_index == -1:
            return

        new_lines.append(import_line.rstrip())

        new_lines.append("")

        new_lines.append(lines[routes_index])

        for i in range(routes_index + 1, len(lines)):
            if lines[i].strip() == "]":
                new_lines.append(routes_entry.rstrip())
                new_lines.append("]")
                new_lines.extend(lines[i + 1 :])
                break
            else:
                new_lines.append(lines[i])

        routes_init_path.write_text("\n".join(new_lines))

    # =========================
    # GENERATE INIT FILE
    # =========================
    def _generate_init_file(self):

        content = """from .route import router

__all__ = ["router"]
"""

        init_path = Path(self.context.route_file_path).parent / "__init__.py"
        init_path.write_text(content)

    # =========================
    # GENERATE ROUTE FILE
    # =========================
    def _generate_route_file(self):

        name = self.context.name
        Name = name.capitalize()

        content = f'''from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Any, Literal

from presentation.routes.{name}.deps import *
from presentation.schemas.{name}.create import Create{Name}Schema
from presentation.schemas.{name}.update import Update{Name}Schema
from presentation.schemas.{name}.response import {Name}Schema
from nova_api_core.presentation.schemas.response import (
    APIResponse,
    default_error_responses,
    PaginatedResponseSchema,
)
from nova_api_core.core.domain.entities.database.sort import Sort
from nova_api_core.core.domain.entities.database.filter import Filter

# USE CASES (for type hints)
from core.use_cases.{name}.get_all import Get{Name}UseCase
from core.use_cases.{name}.get_by_id import Get{Name}ByIdUseCase
from core.use_cases.{name}.create import Create{Name}UseCase
from core.use_cases.{name}.update import Update{Name}UseCase
from core.use_cases.{name}.delete import Delete{Name}UseCase


router = APIRouter(prefix="/{name}", tags=["{name}"])


# =========================
# GET ALL (PAGINATION)
# =========================
@router.get(
    "",
    response_model=APIResponse[PaginatedResponseSchema[{Name}Schema]],
    responses=default_error_responses,
)
async def get_{name}s(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    sort_field: str | None = Query(None, description="Field name to sort by (e.g., 'name', 'created_at')"),
    sort_direction: str = Query("asc", description="Sort direction: 'asc' or 'desc'"),
    filters: str | None = Query(
        None,
        description="JSON array of filter objects [{{field, operator, value, db_operator}}]. Operators: equals, not_equals, like, ilike, in, gt, gte, lt, lte",
        examples={{
            "simple": '[{{"field":"status","operator":"equals","value":"active"}}]',
            "multiple": '[{{"field":"status","operator":"equals","value":"active"}},{{"field":"age","operator":"gte","value":18}}]',
        }},
    ),
    use_case: Get{Name}UseCase = Depends(get_{name}_use_case),
    session=Depends(get_db_session),
):
    """
    List all {name} with pagination, sorting and filtering.
    See query parameters below for filtering and sorting options.
    """
    import json

    sort = None
    if sort_field:
        sort = Sort(field=sort_field, direction=sort_direction)

    filter_objects = None
    if filters:
        try:
            filters_data = json.loads(filters)
            filter_objects = [
                Filter(
                    field=f["field"],
                    operator=f["operator"],
                    value=f["value"],
                    db_operator=f.get("db_operator", "AND"),
                )
                for f in filters_data
            ]
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    result = await use_case.execute(
        session=session,
        skip=skip,
        limit=limit,
        sort=sort,
        filters=filter_objects,
    )

    return APIResponse(
        status_code=200,
        message="Ressources récupérées avec succès",
        content=result,
    )


# =========================
# GET BY ID
# =========================
@router.get(
    "/{{id}}",
    response_model=APIResponse[{Name}Schema],
    responses=default_error_responses,
)
async def get_{name}_by_id(
    id: str,
    use_case: Get{Name}ByIdUseCase = Depends(get_{name}_by_id_use_case),
    session=Depends(get_db_session),
):
    result = await use_case.execute(session, id)

    return APIResponse(
        status_code=200,
        message="Ressource récupérée avec succès",
        content=result,
    )


# =========================
# CREATE
# =========================
@router.post(
    "",
    response_model=APIResponse[{Name}Schema],
    responses=default_error_responses,
)
async def create_{name}(
    data: Create{Name}Schema,
    use_case: Create{Name}UseCase = Depends(create_{name}_use_case),
    session=Depends(get_db_session),
):
    result = await use_case.execute(session, data.model_dump())

    return APIResponse(
        status_code=201,
        message="Ressource créée avec succès",
        content=result,
    )


# =========================
# UPDATE
# =========================
@router.put(
    "/{{id}}",
    response_model=APIResponse[{Name}Schema],
    responses=default_error_responses,
)
async def update_{name}(
    id: str,
    data: Update{Name}Schema,
    use_case: Update{Name}UseCase = Depends(update_{name}_use_case),
    session=Depends(get_db_session),
):
    result = await use_case.execute(session, id, data.model_dump(exclude_unset=True))

    return APIResponse(
        status_code=200,
        message="Ressource mise à jour avec succès",
        content=result,
    )


# =========================
# DELETE
# =========================
@router.delete(
    "/{{id}}",
    response_model=APIResponse[None],
    responses=default_error_responses,
)
async def delete_{name}(
    id: str,
    use_case: Delete{Name}UseCase = Depends(delete_{name}_use_case),
    session=Depends(get_db_session),
):
    await use_case.execute(session, id)

    return APIResponse(
        status_code=200,
        message="Ressource supprimée avec succès",
        content=None,
    )
'''

        Path(self.context.route_file_path).write_text(content)
