from fastapi import APIRouter
from fastapi.testclient import TestClient

from nova_api_core.core.types.error import ErrorResponse
from nova_api_core.presentation.app_factory import create_app
from tests.unit.test_app_factory import FakeBootstrap, FakeConfig, FakeDB, FakeLogger


def test_create_app_basic():
    app = create_app(
        config=FakeConfig(),
        bootstrap=FakeBootstrap(),
        logger=FakeLogger(),
    )

    assert app is not None
    assert app.title == "Test App"


def test_app_state():
    logger = FakeLogger()
    db = FakeDB()

    app = create_app(
        config=FakeConfig(),
        bootstrap=FakeBootstrap(),
        logger=logger,
        db_manager=db,
    )

    assert app.state.logger is logger
    assert app.state.db is db


def test_routes_registration():
    router = APIRouter()

    @router.get("/ping")
    def ping():
        return {"ok": True}

    app = create_app(
        config=FakeConfig(),
        bootstrap=FakeBootstrap(),
        logger=FakeLogger(),
        routes=[router],
    )

    paths = [route.path for route in app.routes]
    assert "/ping" in paths


def test_lifecycle():
    logger = FakeLogger()
    db = FakeDB()

    with TestClient(
        create_app(
            config=FakeConfig(),
            bootstrap=FakeBootstrap(),
            logger=logger,
            db_manager=db,
        )
    ) as client:
        pass

    assert db.connected is True
    assert db.disconnected is True


class CustomException(Exception):
    pass


class CustomExceptionHandler:
    exception = CustomException

    def handle(self, error, logger):
        return ErrorResponse(
            status_code=400,
            message="test error",
        )


def test_error_handler():
    router = APIRouter()

    @router.get("/error")
    def raise_error():
        raise CustomException()

    app = create_app(
        config=FakeConfig(),
        bootstrap=FakeBootstrap(),
        logger=FakeLogger(),
        routes=[router],
        error_handlers=[CustomExceptionHandler()],
    )

    client = TestClient(app)
    res = client.get("/error")

    assert res.status_code == 400
    assert res.json()["message"] == "test error"
