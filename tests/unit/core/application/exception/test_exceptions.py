import pytest

from nova_api_core.core.application.exception.base import AppException
from nova_api_core.core.application.exception.exception import (
    AuthException,
    ConfigurationException,
    DatabaseException,
    NotFoundException,
)


# =========================
# Helpers
# =========================
def assert_exception_common(exc, expected_status, expected_title, message, details):
    assert isinstance(exc, AppException)
    assert exc.status_code == expected_status
    assert exc.message == message

    # Check technical details format
    expected_details = f"[{expected_title}] {details}"
    assert exc.technical_details == expected_details


# =========================
# Tests
# =========================


def test_database_exception():
    exc = DatabaseException(
        message="DB failed",
        technical_details="connection timeout",
    )

    assert_exception_common(
        exc,
        expected_status=500,
        expected_title="DATABASE ERROR",
        message="DB failed",
        details="connection timeout",
    )


def test_not_found_exception():
    exc = NotFoundException(
        message="User not found",
        technical_details="user_id=1",
    )

    assert_exception_common(
        exc,
        expected_status=404,
        expected_title="NOT FOUND",
        message="User not found",
        details="user_id=1",
    )


def test_auth_exception():
    exc = AuthException(
        message="Unauthorized",
        technical_details="missing token",
    )

    assert_exception_common(
        exc,
        expected_status=401,
        expected_title="AUTH ERROR",
        message="Unauthorized",
        details="missing token",
    )


def test_configuration_exception():
    exc = ConfigurationException(
        message="Bad config",
        technical_details="missing env",
    )

    assert_exception_common(
        exc,
        expected_status=500,
        expected_title="CONFIGURATION ERROR",
        message="Bad config",
        details="missing env",
    )
