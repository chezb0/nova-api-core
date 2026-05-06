from dataclasses import dataclass


@dataclass(frozen=True)
class BootstrapConfig:
    APP_NAME: str
    APP_VERSION: str
    ENV: str  # 🔥 dev | prod | test | etc
    LOG_LEVEL: str
    LOG_OUTPUT: str
    LOG_FILE_PATH: str | None = None

    # 🔐 Vault (optional)
    VAULT_URL: str | None = None
    VAULT_ROLE_ID: str | None = None
    VAULT_SECRET_ID: str | None = None
