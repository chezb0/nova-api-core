import pytest
from nova_api_core.core.application.exception.exception import (
    DatabaseException,
)
from nova_api_core.infra.db.sqlalchemy.database_manager import (
    SQLAlchemyDatabaseManager,
)

# =========================
# CONNECT / DISCONNECT
# =========================
@pytest.mark.asyncio
async def test_connect_and_disconnect():
    db = SQLAlchemyDatabaseManager(
        database_url="sqlite+aiosqlite:///:memory:",
    )

    await db.connect()
    await db.disconnect()


# =========================
# SESSION RETRIEVE
# =========================
@pytest.mark.asyncio
async def test_get_session():
    db = SQLAlchemyDatabaseManager(
        database_url="sqlite+aiosqlite:///:memory:",
    )

    await db.connect()

    # Changement du nom de la méthode ici
    async with db.get_session() as session:
        assert session is not None

    await db.disconnect()


# =========================
# INVALID DATABASE URL
# =========================
@pytest.mark.asyncio
async def test_invalid_database_connection():
    # SQLAlchemy lève une erreur si le driver est inconnu
    db = SQLAlchemyDatabaseManager(
        database_url="invalid://test",
    )

    with pytest.raises(DatabaseException) as exc:
        await db.connect()

    assert (
        exc.value.message
        == "Impossible de se connecter à la base de données"
    )


# =========================
# SESSION FAILURE
# =========================
@pytest.mark.asyncio
async def test_session_failure_cleanup():
    db = SQLAlchemyDatabaseManager(
        database_url="sqlite+aiosqlite:///:memory:",
        max_session_retries=2,
        retry_delay_seconds=0.1
    )

    await db.connect()

    # On vérifie que lever une exception dans le bloc utilisateur 
    # est bien catché et transformé en DatabaseException
    with pytest.raises(DatabaseException) as exc:
        async with db.get_session():
            raise Exception("boom")

    assert (
        exc.value.message
        == "Une erreur est survenue lors de la récupération de la session de base de données"
    )
    
    # Vérification que les détails techniques contiennent bien notre erreur originale
    assert "boom" in exc.value.technical_details

    await db.disconnect()