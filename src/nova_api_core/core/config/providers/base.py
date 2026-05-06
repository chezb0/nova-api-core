from typing import Any, Protocol


class ConfigProvider(Protocol):
    def load(self) -> dict[str, Any]: ...
