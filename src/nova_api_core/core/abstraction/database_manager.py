from contextlib import AbstractContextManager
from typing import Protocol


class DatabaseSession(Protocol):
    pass


class DatabaseManager(Protocol):

    async def connect(self) -> None:
        pass

    def get_session(self) -> AbstractContextManager[DatabaseSession]:
        pass

    async def disconnect(self) -> None:
        pass
