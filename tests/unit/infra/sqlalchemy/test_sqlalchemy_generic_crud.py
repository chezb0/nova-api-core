import pytest
import pytest_asyncio
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from nova_api_core.core.application.exception.exception import (
    DatabaseException,
    NotFoundException,
)
from nova_api_core.core.domain.entities.database.filter import Filter
from nova_api_core.core.domain.entities.database.pagination import (
    PaginatedResult,
)
from nova_api_core.core.domain.entities.database.sort import Sort
from nova_api_core.infra.db.sqlalchemy.sqlalchemy_generic_crud import (
    SQLAlchemyGenericCRUD,
)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)


@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_local = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    session = async_session_local()

    try:
        yield session
        await session.commit()
    finally:
        await session.close()
        await engine.dispose()


@pytest.fixture
def crud():
    return SQLAlchemyGenericCRUD(User)


# =========================
# CREATE
# =========================
@pytest.mark.asyncio
async def test_create_single(async_session, crud):
    result = await crud.create(
        async_session,
        data={"name": "John", "email": "john@example.com", "age": 30},
    )

    assert result.id is not None
    assert result.name == "John"
    assert result.email == "john@example.com"
    assert result.age == 30


@pytest.mark.asyncio
async def test_create_multiple(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "John", "email": "john@example.com"},
    )
    await crud.create(
        async_session,
        data={"name": "Jane", "email": "jane@example.com"},
    )

    result = await crud.get(async_session)
    assert result.total == 2
    assert len(result.data) == 2


@pytest.mark.asyncio
async def test_create_invalid_data(async_session, crud):
    with pytest.raises(DatabaseException):
        await crud.create(
            async_session,
            data={"invalid_field": "value"},
        )


# =========================
# GET BY ID
# =========================
@pytest.mark.asyncio
async def test_get_by_id(async_session, crud):
    created = await crud.create(
        async_session,
        data={"name": "John", "email": "john@example.com"},
    )

    result = await crud.get_by_id(async_session, created.id)

    assert result is not None
    assert result.id == created.id
    assert result.name == "John"


@pytest.mark.asyncio
async def test_get_by_id_not_found(async_session, crud):
    result = await crud.get_by_id(async_session, 999)
    assert result is None


# =========================
# GET (PAGINATED)
# =========================
@pytest.mark.asyncio
async def test_get_all(async_session, crud):
    for i in range(3):
        await crud.create(
            async_session,
            data={"name": f"User{i}", "email": f"user{i}@example.com"},
        )

    result = await crud.get(async_session)

    assert isinstance(result, PaginatedResult)
    assert result.total == 3
    assert len(result.data) == 3


@pytest.mark.asyncio
async def test_get_with_skip_limit(async_session, crud):
    for i in range(10):
        await crud.create(
            async_session,
            data={"name": f"User{i}", "email": f"user{i}@example.com"},
        )

    result = await crud.get(async_session, skip=5, limit=3)

    assert result.total == 10
    assert len(result.data) == 3


@pytest.mark.asyncio
async def test_get_with_limit_exceeds_total(async_session, crud):
    for i in range(3):
        await crud.create(
            async_session,
            data={"name": f"User{i}", "email": f"user{i}@example.com"},
        )

    result = await crud.get(async_session, skip=0, limit=100)

    assert result.total == 3
    assert len(result.data) == 3


@pytest.mark.asyncio
async def test_get_empty(async_session, crud):
    result = await crud.get(async_session)

    assert result.total == 0
    assert len(result.data) == 0


# =========================
# GET WITH SORT
# =========================
@pytest.mark.asyncio
async def test_get_with_sort_ascending(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "Charlie", "email": "charlie@example.com", "age": 25},
    )
    await crud.create(
        async_session,
        data={"name": "Alice", "email": "alice@example.com", "age": 30},
    )
    await crud.create(
        async_session,
        data={"name": "Bob", "email": "bob@example.com", "age": 20},
    )

    result = await crud.get(async_session, sort=Sort(field="name", direction="asc"))

    assert len(result.data) == 3
    assert result.data[0].name == "Alice"
    assert result.data[1].name == "Bob"
    assert result.data[2].name == "Charlie"


@pytest.mark.asyncio
async def test_get_with_sort_descending(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "Charlie", "email": "charlie@example.com", "age": 25},
    )
    await crud.create(
        async_session,
        data={"name": "Alice", "email": "alice@example.com", "age": 30},
    )
    await crud.create(
        async_session,
        data={"name": "Bob", "email": "bob@example.com", "age": 20},
    )

    result = await crud.get(async_session, sort=Sort(field="name", direction="desc"))

    assert len(result.data) == 3
    assert result.data[0].name == "Charlie"
    assert result.data[1].name == "Bob"
    assert result.data[2].name == "Alice"


@pytest.mark.asyncio
async def test_get_with_sort_invalid_field(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "John", "email": "john@example.com"},
    )

    with pytest.raises(DatabaseException) as exc:
        await crud.get(async_session, sort=Sort(field="invalid_field"))

    assert "Le champ de tri est invalide" in exc.value.message


# =========================
# GET WITH FILTERS
# =========================
@pytest.mark.asyncio
async def test_get_with_filter_equals(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "John", "email": "john@example.com"},
    )
    await crud.create(
        async_session,
        data={"name": "Jane", "email": "jane@example.com"},
    )

    result = await crud.get(
        async_session,
        filters=[Filter(field="name", operator="equals", value="John")],
    )

    assert result.total == 1
    assert len(result.data) == 1
    assert result.data[0].name == "John"


@pytest.mark.asyncio
async def test_get_with_filter_not_equals(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "John", "email": "john@example.com"},
    )
    await crud.create(
        async_session,
        data={"name": "Jane", "email": "jane@example.com"},
    )

    result = await crud.get(
        async_session,
        filters=[Filter(field="name", operator="not_equals", value="John")],
    )

    assert len(result.data) == 1
    assert result.data[0].name == "Jane"


@pytest.mark.asyncio
async def test_get_with_filter_like(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "Johnny", "email": "johnny@example.com"},
    )
    await crud.create(
        async_session,
        data={"name": "Jane", "email": "jane@example.com"},
    )

    result = await crud.get(
        async_session,
        filters=[Filter(field="name", operator="like", value="John")],
    )

    assert len(result.data) == 1
    assert result.data[0].name == "Johnny"


@pytest.mark.asyncio
async def test_get_with_filter_ilike(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "Johnny", "email": "johnny@example.com"},
    )
    await crud.create(
        async_session,
        data={"name": "JANE", "email": "jane@example.com"},
    )

    result = await crud.get(
        async_session,
        filters=[Filter(field="name", operator="ilike", value="jane")],
    )

    assert len(result.data) == 1
    assert result.data[0].name == "JANE"


@pytest.mark.asyncio
async def test_get_with_filter_in(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "John", "email": "john@example.com"},
    )
    await crud.create(
        async_session,
        data={"name": "Jane", "email": "jane@example.com"},
    )
    await crud.create(
        async_session,
        data={"name": "Bob", "email": "bob@example.com"},
    )

    result = await crud.get(
        async_session,
        filters=[
            Filter(field="name", operator="in", value=["John", "Jane"])
        ],
    )

    assert len(result.data) == 2


@pytest.mark.asyncio
async def test_get_with_filter_gt(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "User1", "email": "user1@example.com", "age": 20},
    )
    await crud.create(
        async_session,
        data={"name": "User2", "email": "user2@example.com", "age": 30},
    )
    await crud.create(
        async_session,
        data={"name": "User3", "email": "user3@example.com", "age": 25},
    )

    result = await crud.get(
        async_session,
        filters=[Filter(field="age", operator="gt", value=25)],
    )

    assert len(result.data) == 1
    assert result.data[0].age == 30


@pytest.mark.asyncio
async def test_get_with_filter_gte(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "User1", "email": "user1@example.com", "age": 20},
    )
    await crud.create(
        async_session,
        data={"name": "User2", "email": "user2@example.com", "age": 30},
    )
    await crud.create(
        async_session,
        data={"name": "User3", "email": "user3@example.com", "age": 25},
    )

    result = await crud.get(
        async_session,
        filters=[Filter(field="age", operator="gte", value=25)],
    )

    assert len(result.data) == 2


@pytest.mark.asyncio
async def test_get_with_filter_lt(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "User1", "email": "user1@example.com", "age": 20},
    )
    await crud.create(
        async_session,
        data={"name": "User2", "email": "user2@example.com", "age": 30},
    )

    result = await crud.get(
        async_session,
        filters=[Filter(field="age", operator="lt", value=25)],
    )

    assert len(result.data) == 1
    assert result.data[0].age == 20


@pytest.mark.asyncio
async def test_get_with_filter_lte(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "User1", "email": "user1@example.com", "age": 20},
    )
    await crud.create(
        async_session,
        data={"name": "User2", "email": "user2@example.com", "age": 30},
    )
    await crud.create(
        async_session,
        data={"name": "User3", "email": "user3@example.com", "age": 25},
    )

    result = await crud.get(
        async_session,
        filters=[Filter(field="age", operator="lte", value=25)],
    )

    assert len(result.data) == 2


@pytest.mark.asyncio
async def test_get_with_multiple_and_filters(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "John", "email": "john@example.com", "age": 30},
    )
    await crud.create(
        async_session,
        data={"name": "Jane", "email": "jane@example.com", "age": 25},
    )
    await crud.create(
        async_session,
        data={"name": "Bob", "email": "bob@example.com", "age": 30},
    )

    result = await crud.get(
        async_session,
        filters=[
            Filter(field="name", operator="equals", value="John", db_operator="AND"),
            Filter(field="age", operator="equals", value=30, db_operator="AND"),
        ],
    )

    assert len(result.data) == 1
    assert result.data[0].name == "John"


@pytest.mark.asyncio
async def test_get_with_or_filters(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "John", "email": "john@example.com"},
    )
    await crud.create(
        async_session,
        data={"name": "Jane", "email": "jane@example.com"},
    )
    await crud.create(
        async_session,
        data={"name": "Bob", "email": "bob@example.com"},
    )

    result = await crud.get(
        async_session,
        filters=[
            Filter(field="name", operator="equals", value="John", db_operator="OR"),
            Filter(field="name", operator="equals", value="Jane", db_operator="OR"),
        ],
    )

    assert len(result.data) == 2


@pytest.mark.asyncio
async def test_get_with_invalid_filter_field(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "John", "email": "john@example.com"},
    )

    with pytest.raises(DatabaseException):
        await crud.get(
            async_session,
            filters=[
                Filter(field="invalid_field", operator="equals", value="test")
            ],
        )


# =========================
# UPDATE
# =========================
@pytest.mark.asyncio
async def test_update(async_session, crud):
    created = await crud.create(
        async_session,
        data={"name": "John", "email": "john@example.com", "age": 30},
    )

    result = await crud.update(
        async_session,
        created.id,
        data={"name": "Jane", "age": 25},
    )

    assert result.id == created.id
    assert result.name == "Jane"
    assert result.age == 25
    assert result.email == "john@example.com"


@pytest.mark.asyncio
async def test_update_not_found(async_session, crud):
    with pytest.raises(NotFoundException) as exc:
        await crud.update(
            async_session,
            999,
            data={"name": "Jane"},
        )

    assert "Ressource introuvable" in exc.value.message


@pytest.mark.asyncio
async def test_update_partial(async_session, crud):
    created = await crud.create(
        async_session,
        data={"name": "John", "email": "john@example.com", "age": 30},
    )

    result = await crud.update(
        async_session,
        created.id,
        data={"name": "John Updated"},
    )

    assert result.name == "John Updated"
    assert result.email == "john@example.com"
    assert result.age == 30


# =========================
# DELETE
# =========================
@pytest.mark.asyncio
async def test_delete(async_session, crud):
    created = await crud.create(
        async_session,
        data={"name": "John", "email": "john@example.com"},
    )

    await crud.delete(async_session, created.id)

    result = await crud.get_by_id(async_session, created.id)
    assert result is None


@pytest.mark.asyncio
async def test_delete_not_found(async_session, crud):
    with pytest.raises(NotFoundException) as exc:
        await crud.delete(async_session, 999)

    assert "Ressource introuvable" in exc.value.message


@pytest.mark.asyncio
async def test_delete_multiple_and_verify(async_session, crud):
    await crud.create(
        async_session,
        data={"name": "User1", "email": "user1@example.com"},
    )
    await crud.create(
        async_session,
        data={"name": "User2", "email": "user2@example.com"},
    )

    result = await crud.get(async_session)
    assert result.total == 2

    user_id = result.data[0].id
    await crud.delete(async_session, user_id)

    result = await crud.get(async_session)
    assert result.total == 1


# =========================
# COMPLEX SCENARIOS
# =========================
@pytest.mark.asyncio
async def test_combined_filters_sort_pagination(async_session, crud):
    for i in range(20):
        await crud.create(
            async_session,
            data={
                "name": f"User{i}",
                "email": f"user{i}@example.com",
                "age": 20 + (i % 10),
            },
        )

    result = await crud.get(
        async_session,
        skip=5,
        limit=5,
        filters=[
            Filter(field="age", operator="gte", value=25, db_operator="AND")
        ],
        sort=Sort(field="name", direction="desc"),
    )

    assert result.total == 10
    assert len(result.data) == 5


# =========================
# EXECUTE SQL
# =========================
@pytest.mark.asyncio
async def test_execute_sql(async_session, crud):

    await crud.create(
        async_session,
        data={
            "name": "John",
            "email": "john@example.com",
            "age": 30,
        },
    )

    result = await crud.execute_sql(
        session=async_session,
        sql="""
            SELECT *
            FROM users
            WHERE email = :email
        """,
        params={
            "email": "john@example.com",
        },
    )

    row = result.mappings().first()

    assert row is not None
    assert row["name"] == "John"
    assert row["email"] == "john@example.com"
    assert row["age"] == 30
