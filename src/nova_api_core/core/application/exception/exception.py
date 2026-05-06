from .base import AppException


class DatabaseException(AppException):
    TITLE = "DATABASE ERROR"

    def __init__(
        self,
        message: str = "Erreur liée à la base de données",
        technical_details: str | None = None,
    ):
        super().__init__(
            message=message,
            technical_details=technical_details,
            status_code=500,
        )


class NotFoundException(AppException):
    TITLE = "NOT FOUND"

    def __init__(
        self,
        message: str = "Ressource non trouvée",
        technical_details: str | None = None,
    ):
        super().__init__(
            message=message,
            technical_details=technical_details,
            status_code=404,
        )


class AuthException(AppException):
    TITLE = "AUTH ERROR"

    def __init__(
        self,
        message: str = "Accès non autorisé",
        technical_details: str | None = None,
    ):
        super().__init__(
            message=message,
            technical_details=technical_details,
            status_code=401,
        )


class ConfigurationException(AppException):
    TITLE = "CONFIGURATION ERROR"

    def __init__(
        self,
        message: str = "Erreur de configuration",
        technical_details: str | None = None,
    ):
        super().__init__(
            message=message,
            technical_details=technical_details,
            status_code=500,
        )
