import asyncio
from contextlib import asynccontextmanager
from typing import Any, Optional

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
    ) -> None:
        self.database_url = database_url
        self.database_name = database_name
        self.max_session_retries = max_session_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.client: Optional[AsyncIOMotorClient[Any]] = None
        self.db: Optional[Any] = None

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
    async def get_session(self):  # type: ignore[no-untyped-def, override]
        if self.client is None:
            await self.connect()

        last_exception: Optional[Exception] = None
        for attempt in range(1, self.max_session_retries + 1):
            try:
                assert self.client is not None
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
            assert self.db is not None
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
