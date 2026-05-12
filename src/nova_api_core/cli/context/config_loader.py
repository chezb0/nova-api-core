import json
from pathlib import Path
from typing import Any, Dict

from nova_api_core.core.application.exception.exception import DatabaseException


# =========================
# LOAD NOVA CONFIG
# =========================
def load_nova_config() -> Dict[str, Any]:
    try:
        config_path = Path.cwd() / "nova_core.json"

        if not config_path.exists():
            raise DatabaseException(
                message="Projet Nova invalide",
                technical_details="nova_core.json file not found at project root",
            )

        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)

        required_fields = ["project_name", "database"]

        for field in required_fields:
            if field not in config:
                raise DatabaseException(
                    message="Configuration Nova invalide",
                    technical_details=f"Missing required field in nova_core.json: {field}",
                )

        return config

    except DatabaseException:
        raise

    except Exception as e:
        raise DatabaseException(
            message="Impossible de charger la configuration Nova",
            technical_details=str(e),
        )
