import asyncio
from contextlib import asynccontextmanager

from motor.motor_asyncio import AsyncIOMotorClient

from nova_api_core.core.abstraction.database_manager import DatabaseManager
from nova_api_core.core.application.exception.exception import (
    DatabaseException,
)


class MongoDatabaseManager(DatabaseManager):
    def __init__(
        self,
        *,
        database_url: str,
        database_name: str,
        max_session_retries: int = 3,
        retry_delay_seconds: float = 1.0,
    ):
        self.database_url = database_url
        self.database_name = database_name
        self.max_session_retries = max_session_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.client = None
        self.db = None

    async def connect(self) -> None:
        try:
            self.client = AsyncIOMotorClient(self.database_url)
            await self.client.admin.command("ping")
            self.db = self.client[self.database_name]
        except Exception as e:
            raise DatabaseException(
                message="Impossible de se connecter à la base de données MongoDB",
                technical_details=str(e),
            )

    @asynccontextmanager
    async def get_session(self):
        if self.client is None:
            await self.connect()

        for attempt in range(1, self.max_session_retries + 1):
            try:
                await self.client.admin.command("ping")
                break
            except Exception as e:
                last_exception = e
                if attempt == self.max_session_retries:
                    raise DatabaseException(
                        message="La connexion à MongoDB a été perdue",
                        technical_details=str(last_exception),
                    )
                await asyncio.sleep(self.retry_delay_seconds)

        try:
            # Ici, 'self.db' fait office de session/handle pour MongoDB
            yield self.db
        except Exception as e:
            raise DatabaseException(
                message="Une erreur est survenue lors de l'accès à MongoDB",
                technical_details=str(e),
            )

    async def disconnect(self) -> None:
        if self.client:
            try:
                self.client.close()
                self.client = None
                self.db = None
            except Exception as e:
                raise DatabaseException(
                    message="Impossible de fermer correctement la connexion MongoDB",
                    technical_details=str(e),
                )
