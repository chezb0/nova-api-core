from typing import Any

import hvac

from nova_api_core.core.application.exception.exception import ConfigurationException


class VaultProvider:
    def __init__(
        self,
        *,
        url: str,
        role_id: str | None,
        secret_id: str | None,
        secret_path: str,
    ):
        self.url = url
        self.role_id = role_id
        self.secret_id = secret_id
        self.secret_path = secret_path

    def load(self) -> dict[str, Any]:
        try:
            client = hvac.Client(url=self.url)

            # 🔐 Authenticate with AppRole
            if not self.role_id or not self.secret_id:
                raise ConfigurationException(
                    message="Vault credentials missing",
                    technical_details="role_id or secret_id is None",
                )

            client.auth.approle.login(
                role_id=self.role_id,
                secret_id=self.secret_id,
            )

            if not client.is_authenticated():
                raise ConfigurationException(
                    message="Vault authentication failed",
                    technical_details="Invalid credentials",
                )

            # 📦 Read secret (KV v2)
            response = client.secrets.kv.v2.read_secret_version(path=self.secret_path)

            data: dict[str, Any] = response["data"]["data"]
            return data

        except ConfigurationException:
            raise

        except Exception as e:
            raise ConfigurationException(
                message="Vault provider error",
                technical_details=str(e),
            )
