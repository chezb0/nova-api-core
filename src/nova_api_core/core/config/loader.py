from dataclasses import fields, is_dataclass
from typing import Any, Type, TypeVar, Union, cast, get_args, get_origin

from nova_api_core.core.application.exception.exception import ConfigurationException
from nova_api_core.core.config.bootstrap import BootstrapConfig
from nova_api_core.core.config.providers.base import ConfigProvider

T = TypeVar("T", bound=object)


class ConfigLoader:

    # =========================
    # BOOTSTRAP
    # =========================
    @staticmethod
    def load_bootstrap(provider: ConfigProvider) -> BootstrapConfig:
        data = provider.load()

        try:
            return BootstrapConfig(
                APP_NAME=data["APP_NAME"],
                APP_VERSION=data["APP_VERSION"],
                ENV=data.get("ENV", "dev").lower(),
                LOG_LEVEL=data.get("LOG_LEVEL", "INFO"),
                LOG_OUTPUT=data.get("LOG_OUTPUT", "CONSOLE"),
                LOG_FILE_PATH=data.get("LOG_FILE_PATH"),
                VAULT_URL=data.get("VAULT_URL"),
                VAULT_ROLE_ID=data.get("VAULT_ROLE_ID"),
                VAULT_SECRET_ID=data.get("VAULT_SECRET_ID"),
            )
        except KeyError as e:
            raise ConfigurationException(
                message="Missing bootstrap configuration",
                technical_details=str(e),
            )

    # =========================
    # APP CONFIG
    # =========================
    @staticmethod
    def load_app_config(
        config_class: Type[T],
        providers: list[ConfigProvider],
    ) -> T:

        if not is_dataclass(config_class):
            raise ConfigurationException(
                message="Invalid config class",
                technical_details="Must be a dataclass",
            )

        # Load all providers once (perf + consistency)
        data_sources = [p.load() for p in providers]

        def cast_value(name: str, value: Any | None, expected_type: Any) -> Any:

            if value is None:
                raise ConfigurationException(
                    message=f"Missing value for '{name}'",
                    technical_details="Value is None",
                )

            try:
                if get_origin(expected_type) is Union:
                    args = get_args(expected_type)
                    non_none = [t for t in args if t is not type(None)]
                    if non_none:
                        expected_type = non_none[0]

                if expected_type is int:
                    return int(str(value))

                if expected_type is float:
                    return float(str(value))

                if expected_type is bool:
                    return str(value).lower() in ("true", "1", "yes")

                if expected_type is str:
                    return str(value)

                return value

            except Exception:
                raise ConfigurationException(
                    message=f"Invalid type for '{name}'",
                    technical_details=f"Expected {expected_type}, got '{value}'",
                )

        result = {}
        config_fields = fields(cast(type, config_class))
        for f in config_fields:
            key = f.name
            value = None
            found = False

            for source in data_sources:
                if key in source:
                    value = source[key]
                    found = True
                    break

            if not found:
                raise ConfigurationException(
                    message=f"Missing configuration '{key}'",
                    technical_details="Not found in any provider",
                )

            result[key] = cast_value(key, value, f.type)

        return config_class(**result)
