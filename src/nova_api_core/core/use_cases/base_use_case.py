from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from nova_api_core.core.application.exception.base import AppException

T = TypeVar("T")


class BaseUseCase(ABC, Generic[T]):

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> T:
        pass

    # =========================
    # SAFE EXECUTION WRAPPER
    # =========================
    async def run(self, *args: Any, **kwargs: Any) -> T:

        try:
            return await self.execute(*args, **kwargs)

        except AppException:
            raise

        except Exception as e:
            raise AppException(
                message="Use case execution failed",
                technical_details=str(e),
            )
