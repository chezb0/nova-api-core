from pathlib import Path

import typer
from rich import print


def init_command(name: str = typer.Argument(..., help="Project name")) -> None:
    """
    Initialize a fully wired Nova project:

    - BootstrapConfig loaded via EnvProvider
    - AppConfig loaded via ConfigLoader + providers
    - JsonLogger initialized from bootstrap
    - Default ROUTES + ERROR_HANDLERS
    - Health route included
    - Exception handling ready (AppException + Generic)
    """

    project_path = Path.cwd() / name

    if project_path.exists():
        print("[red]Project already exists[/red]")
        raise typer.Exit(code=1)

    print(f"[green]Creating Nova project:[/green] {name}")

    # =========================
    # DIRECTORIES
    # =========================
    (project_path / "core/config").mkdir(parents=True, exist_ok=True)
    (project_path / "infra/logger").mkdir(parents=True, exist_ok=True)
    (project_path / "presentation/routes").mkdir(parents=True, exist_ok=True)
    (project_path / "presentation/exception_handlers").mkdir(
        parents=True, exist_ok=True
    )
    (project_path / "tests").mkdir(parents=True, exist_ok=True)

    for folder in ["core", "infra", "presentation", "tests"]:
        (project_path / folder / "__init__.py").touch()

    # =========================
    # APP CONFIG (USER DOMAIN)
    # =========================
    (project_path / "core/config/app_config.py").write_text(
        '''from dataclasses import dataclass


@dataclass
class AppConfig:
    """
    User application configuration.

    Define your business configuration here.

    Examples:
        DATABASE_URL: str
        REDIS_URL: str
        JWT_SECRET: str
        PORT: int
        DEBUG: bool
    """
    pass
'''
    )

    # =========================
    # BOOTSTRAP WRAPPER
    # =========================
    (project_path / "core/config/bootstrap.py").write_text(
        """from nova_api_core.core.config.bootstrap import BootstrapConfig

# Loaded via ConfigLoader:
# - .env.base
# - .env.{ENV}
# - optional Vault provider
"""
    )

    # =========================
    # LOGGER WRAPPER
    # =========================
    (project_path / "infra/logger/json_logger.py").write_text(
        """from nova_api_core.infra.logger.json_logger import JsonLogger

# Structured logger:
# - timestamp
# - level
# - message
# - data
# - environment
# - app_name

# Optional bootstrap-driven config:
# log_level
# log_output
# log_file_path
"""
    )

    # =========================
    # HEALTH ROUTE
    # =========================
    (project_path / "presentation/routes/health.py").write_text(
        """from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "nova-app"
    }
"""
    )

    # =========================
    # ROUTES REGISTRY
    # =========================
    (project_path / "presentation/routes/__init__.py").write_text(
        """from .health import router as health_router

ROUTES = [
    health_router,
]
"""
    )

    # =========================
    # ERROR HANDLERS
    # =========================
    (
        project_path / "presentation/exception_handlers/app_exception_handler.py"
    ).write_text(
        """from nova_api_core.presentation.exception_handlers.app_exception_handler import AppExceptionHandler
"""
    )

    (
        project_path / "presentation/exception_handlers/generic_exception_handler.py"
    ).write_text(
        """from nova_api_core.presentation.exception_handlers.generic_exception_handler import GenericExceptionHandler
"""
    )

    (project_path / "presentation/exception_handlers/__init__.py").write_text(
        """from .app_exception_handler import AppExceptionHandler
from .generic_exception_handler import GenericExceptionHandler

ERROR_HANDLERS = [
    AppExceptionHandler(),
    GenericExceptionHandler(),
]
"""
    )

    # =========================
    # APP ENTRYPOINT (REAL WIRING)
    # =========================
    (project_path / "app.py").write_text(
        """from nova_api_core.presentation.app_factory import create_app

from nova_api_core.core.config.loader import ConfigLoader
from nova_api_core.core.config.providers.env_provider import EnvProvider

from infra.logger.json_logger import JsonLogger
from presentation.routes import ROUTES
from presentation.exception_handlers import ERROR_HANDLERS

from core.config.app_config import AppConfig


# =========================
# BOOTSTRAP LOAD
# =========================
bootstrap_provider = EnvProvider(".env.base")
bootstrap = ConfigLoader.load_bootstrap(bootstrap_provider)

# =========================
# ENV LOAD (DYNAMIC)
# =========================
env_provider = EnvProvider(f".env.{bootstrap.ENV}")

# =========================
# APP CONFIG LOAD
# =========================
providers = [
    env_provider,
    # future: VaultProvider()
]

config = ConfigLoader.load_app_config(
    AppConfig,
    providers=providers,
)

# =========================
# LOGGER
# =========================
logger = JsonLogger(
    app_name=bootstrap.APP_NAME,
    environment=bootstrap.ENV,

    # =========================
    # OPTIONAL (BOOTSTRAP DRIVEN)
    # =========================
    # log_level=bootstrap.LOG_LEVEL,
    # log_output=bootstrap.LOG_OUTPUT,
    # log_file_path=bootstrap.LOG_FILE_PATH,
)

# =========================
# APP CREATION
# =========================
app = create_app(
    config=config,
    bootstrap=bootstrap,
    logger=logger,
    routes=ROUTES,
    error_handlers=ERROR_HANDLERS,
)
"""
    )

    # =========================
    # ENV FILES
    # =========================
    (project_path / ".env.base").write_text("""APP_NAME=MyApp
APP_VERSION=0.1.0
ENV=dev
LOG_LEVEL=DEBUG
LOG_OUTPUT=CONSOLE
""")

    (project_path / ".env.dev").write_text("""DEBUG=true
""")

    # =========================
    # PYPROJECT
    # =========================
    (project_path / "pyproject.toml").write_text(f"""[project]
name = "{name}"
version = "0.1.0"
""")

    print("[green]✔ Nova project created successfully[/green]")
    print("[cyan]✔ Bootstrap + Config + Logger + Routes + ErrorHandlers wired[/cyan]")
