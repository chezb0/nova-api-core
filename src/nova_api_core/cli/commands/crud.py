import typer
from rich import print

from nova_api_core.cli.generators.context.crud_context_builder import (
    CrudContextBuilder,
)
from nova_api_core.cli.generators.deps_generator import DepsGenerator
from nova_api_core.cli.generators.model_generator import ModelGenerator
from nova_api_core.cli.generators.route_generator import RouteGenerator
from nova_api_core.cli.generators.schema_generator import SchemaGenerator
from nova_api_core.cli.generators.use_case_generator import UseCaseGenerator


def crud_command(name: str) -> None:

    try:

        print(f"[green]🚀 Generating CRUD for '{name}'...[/green]")

        # =========================
        # BUILD CONTEXT
        # =========================
        context = CrudContextBuilder(name=name).build()

        # =========================
        # GENERATORS
        # =========================
        generators = [
            ModelGenerator(context),
            SchemaGenerator(context),
            UseCaseGenerator(context),
            DepsGenerator(context),
            RouteGenerator(context),
        ]

        # =========================
        # GENERATE FILES
        # =========================
        for generator in generators:
            generator.generate()

        print(f"[bold green]✅ CRUD '{name}' generated successfully.[/bold green]")

    except Exception as e:
        print(f"[red]Error while generating CRUD:[/red] {str(e)}")
        raise typer.Exit(1)
