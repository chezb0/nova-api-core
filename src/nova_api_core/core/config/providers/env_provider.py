import os
from typing import Any, Optional

from dotenv import load_dotenv


class EnvProvider:
    def __init__(self, env_file: Optional[str] = None):
        self.env_file = env_file

    def load(self) -> dict[str, Any]:
        # Load .env file if provided
        if self.env_file:
            load_dotenv(self.env_file)

        # Return environment variables
        return dict(os.environ)
