class AppException(Exception):
    TITLE = "APPLICATION ERROR"

    def __init__(
        self,
        message: str = "Une erreur est survenue dans le serveur",
        technical_details: str | None = None,
        status_code: int = 500,
    ):
        super().__init__(message)
        self.message = message
        self.technical_details = (
            f"[{self.TITLE}] {technical_details}" if technical_details else None
        )
        self.status_code = status_code
