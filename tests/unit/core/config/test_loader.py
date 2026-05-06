from dataclasses import dataclass

from nova_api_core.core.application.exception.exception import ConfigurationException
from nova_api_core.core.config.bootstrap import BootstrapConfig
from nova_api_core.core.config.loader import ConfigLoader
from tests.unit.core.config.fakes import FakeProvider


def test_load_bootstrap_success():
    provider = FakeProvider(
        {
            "APP_NAME": "Nova",
            "APP_VERSION": "1.0",
            "ENV": "dev",
            "LOG_LEVEL": "DEBUG",
            "LOG_OUTPUT": "CONSOLE",
        }
    )

    bootstrap = ConfigLoader.load_bootstrap(provider)

    assert isinstance(bootstrap, BootstrapConfig)
    assert bootstrap.APP_NAME == "Nova"
    assert bootstrap.ENV == "dev"


def test_load_bootstrap_missing_key():
    provider = FakeProvider(
        {
            "APP_NAME": "Nova",
            # missing APP_VERSION
        }
    )

    try:
        ConfigLoader.load_bootstrap(provider)
        assert False, "Expected ConfigurationException"
    except ConfigurationException as e:
        assert "Missing bootstrap configuration" in str(e)


@dataclass
class DummyConfig:
    PORT: int
    DEBUG: bool
    NAME: str


def test_load_app_config_success():
    provider = FakeProvider(
        {
            "PORT": "8000",
            "DEBUG": "true",
            "NAME": "nova-app",
        }
    )

    config = ConfigLoader.load_app_config(
        DummyConfig,
        providers=[provider],
    )

    assert config.PORT == 8000
    assert config.DEBUG is True
    assert config.NAME == "nova-app"


def test_multi_provider_priority():
    p1 = FakeProvider(
        {
            "PORT": "8000",
            "DEBUG": "true",
            "NAME": "from-env",
        }
    )

    p2 = FakeProvider(
        {
            "PORT": "9000",
            "DEBUG": "false",
            "NAME": "from-vault",
        }
    )

    config = ConfigLoader.load_app_config(
        DummyConfig,
        providers=[p1, p2],
    )

    assert config.NAME == "from-env"
    assert config.PORT == 8000
    assert config.DEBUG is True


def test_invalid_type_cast():
    provider = FakeProvider(
        {
            "PORT": "not-a-number",
            "DEBUG": "true",
            "NAME": "nova",
        }
    )

    try:
        ConfigLoader.load_app_config(
            DummyConfig,
            providers=[provider],
        )
        assert False, "Expected ConfigurationException"
    except ConfigurationException as e:
        assert "Invalid type" in str(e)


def test_missing_config_field():
    provider = FakeProvider(
        {
            "PORT": "8000",
            # DEBUG missing
            "NAME": "nova",
        }
    )

    try:
        ConfigLoader.load_app_config(
            DummyConfig,
            providers=[provider],
        )
        assert False, "Expected ConfigurationException"
    except ConfigurationException:
        pass
