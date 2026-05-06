from nova_api_core.presentation.app_factory import create_app

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
