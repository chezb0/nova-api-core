from contextlib import asynccontextmanager
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from nova_api_core.core.application.exception.exception import (
    DatabaseException,
)

class SQLAlchemyDatabaseManager:
    def __init__(
        self,
        *,
        database_url: str,
        echo: bool = False,
        max_session_retries: int = 3,
        retry_delay_seconds: float = 1.0,
    ):
        self.database_url = database_url
        self.echo = echo
        self.max_session_retries = max_session_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.engine = None
        self.session_factory = None

    async def connect(self) -> None:
        try:
            self.engine = create_async_engine(
                self.database_url,
                echo=self.echo,
            )
            self.session_factory = async_sessionmaker(
                bind=self.engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )

            async with self.engine.begin() as conn:
                await conn.run_sync(lambda _: None)
        except Exception as e:
            raise DatabaseException(
                message="Impossible de se connecter à la base de données",
                technical_details=str(e),
            )

    @asynccontextmanager
    async def get_session(self):
        if not self.session_factory:
            await self.connect()

        session = None
        last_exception = None

        for attempt in range(1, self.max_session_retries + 1):
            try:
                session = self.session_factory()
                await session.execute(text("SELECT 1"))
                break 
            except Exception as e:
                if session:
                    await session.close()
                last_exception = e
                if attempt == self.max_session_retries:
                    raise DatabaseException(
                        message="Une erreur est survenue lors de la récupération de la session de base de données",
                        technical_details=str(last_exception),
                    )
                await asyncio.sleep(self.retry_delay_seconds)

        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise DatabaseException(
                message="Une erreur est survenue lors de la récupération de la session de base de données",
                technical_details=str(e),
            )
        finally:
            await session.close()

    async def disconnect(self) -> None:
        if self.engine:
            try:
                await self.engine.dispose()
            except Exception as e:
                raise DatabaseException(
                    message="Impossible de fermer correctement la connexion à la base de données",
                    technical_details=str(e),
                )