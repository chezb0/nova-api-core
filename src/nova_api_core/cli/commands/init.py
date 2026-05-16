import json
import subprocess
from pathlib import Path

import typer
from rich import print

from nova_api_core.cli.renderers.nova_renderer import NovaRenderer
from nova_api_core.core.types.database_type import DatabaseType


def init_command(name: str, db: DatabaseType) -> None:
    project_path = Path.cwd() / name
    if project_path.exists():
        print(f"[red]Error: Folder {name} already exists.[/red]")
        raise typer.Exit(1)

    renderer = NovaRenderer()
    print(f"[green]🚀 Initializing {name} with {db.value}...[/green]")

    # 1. Création de l'arborescence complète
    folders = [
        "core/config",
        "core/use_cases",
        "core/domain/models",
        "infra/logger",
        "infra/db",
        "presentation/routes",
        "presentation/exception_handlers",
        "tests",
    ]

    for folder in folders:
        path = project_path / folder
        path.mkdir(parents=True, exist_ok=True)

        # Création des __init__.py récursifs pour le packaging
        current = project_path
        for part in folder.split("/"):
            current = current / part
            (current / "__init__.py").touch()

    # 2. Génération et écriture des fichiers racine et config
    (project_path / "app.py").write_text(renderer.render_app_entrypoint(db))
    # (project_path / "pyproject.toml").write_text(renderer.render_pyproject(name))
    (project_path / "requirements.txt").write_text(renderer.render_requirements())
    (project_path / "core/config/app_config.py").write_text(
        renderer.render_app_config(db)
    )

    # Environnement
    (project_path / ".env.base").write_text(renderer.render_bootstrap_env(name))
    (project_path / ".env.dev").write_text(renderer.render_env_content(db, is_dev=True))
    (project_path / ".env.prod").write_text("# Add here your production's variables...")

    # 3. Initialisation des Routes via Templates
    (project_path / "presentation/routes/health.py").write_text(
        renderer.render_structure("health_route", {"APP_NAME": name})
    )
    (project_path / "presentation/routes/__init__.py").write_text(
        renderer.render_structure("routes_init")
    )

    # 4. Initialisation des Handlers via Templates
    (project_path / "presentation/exception_handlers/__init__.py").write_text(
        renderer.render_structure("handlers_init")
    )

    # 5. Git Init & .gitignore
    try:
        subprocess.run(
            ["git", "init"], cwd=project_path, check=True, capture_output=True
        )
        (project_path / ".gitignore").write_text(
            "__pycache__/\n.env*\n.venv/\n*.db\n.pytest_cache/\n"
        )
    except Exception:
        pass

    # =========================
    # NOVA CONFIG
    # =========================
    (project_path / "nova_core.json").write_text(
        json.dumps(
            {
                "project_name": name,
                "database": db.value,
                "nova_api_core_version": "0.1.0",
            },
            indent=4,
        )
    )

    print(f"\n[bold green]✨ Project {name} is ready![/bold green]")
    print("[yellow]Next steps:[/yellow]")
    print(f"  1. cd {name}")
    print(
        "  2. nova crud your_resource (ex: users or you can do that later, full doc: https://gence.bemanjary.com/fr/products/nova-api-core)"
    )
    print("  3. uvicorn app:app --host localhost --port 8001")
