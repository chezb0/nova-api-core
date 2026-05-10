import pytest
from unittest.mock import patch, AsyncMock
from mongomock_motor import AsyncMongoMockClient

from nova_api_core.core.application.exception.exception import (
    DatabaseException,
)
from nova_api_core.infra.db.mongo.mongo_database_manager import MongoDatabaseManager

# =========================
# CONNECT / DISCONNECT
# =========================
@pytest.mark.asyncio
async def test_mongo_connect_and_disconnect():
    # On mock AsyncIOMotorClient pour éviter une tentative de connexion réelle
    with patch("nova_api_core.infra.db.mongo.mongo_database_manager.AsyncIOMotorClient") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.admin.command = AsyncMock(return_value={"ok": 1.0})

        db = MongoDatabaseManager(
            database_url="mongodb://localhost:27017",
            database_name="test_db"
        )

        await db.connect()
        assert db.client is not None
        assert db.db is not None
        
        await db.disconnect()
        assert db.client is None
        assert db.db is None

# =========================
# GET SESSION (DATABASE)
# =========================
@pytest.mark.asyncio
async def test_mongo_get_session_success():
    # Utilisation de mongomock pour un test réaliste sans serveur
    with patch("nova_api_core.infra.db.mongo.mongo_database_manager.AsyncIOMotorClient", AsyncMongoMockClient):
        db = MongoDatabaseManager(
            database_url="mongodb://localhost:27017",
            database_name="test_db"
        )

        async with db.get_session() as mongo_db:
            assert mongo_db is not None
            # On vérifie qu'on pointe sur la bonne base
            assert mongo_db.name == "test_db"

# =========================
# CONNECTION FAILURE
# =========================
@pytest.mark.asyncio
async def test_mongo_invalid_connection():
    db = MongoDatabaseManager(
        database_url="mongodb://invalid_url",
        database_name="test_db"
    )

    # On simule une erreur de ping
    with patch("nova_api_core.infra.db.mongo.mongo_database_manager.AsyncIOMotorClient") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.admin.command = AsyncMock(side_effect=Exception("Connection failed"))

        with pytest.raises(DatabaseException) as exc:
            await db.connect()
        
        assert "Impossible de se connecter à la base de données MongoDB" in exc.value.message

# =========================
# RETRY FAILURE
# =========================
@pytest.mark.asyncio
async def test_mongo_session_retry_failure():
    db = MongoDatabaseManager(
        database_url="mongodb://localhost:27017",
        database_name="test_db",
        max_session_retries=2,
        retry_delay_seconds=0.01
    )

    with patch("nova_api_core.infra.db.mongo.mongo_database_manager.AsyncIOMotorClient") as mock_client:
        mock_instance = mock_client.return_value
        # Le premier ping dans connect() passe, mais les suivants dans get_session échouent
        mock_instance.admin.command = AsyncMock(side_effect=[{"ok": 1}, Exception("Lost connection"), Exception("Lost connection")])

        await db.connect()

        with pytest.raises(DatabaseException) as exc:
            async with db.get_session():
                pass
        
        assert "La connexion à MongoDB a été perdue" in exc.value.message