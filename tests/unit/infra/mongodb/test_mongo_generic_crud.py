import pytest
import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient
from bson import ObjectId

from nova_api_core.core.application.exception.exception import (
    DatabaseException,
    NotFoundException,
)
from nova_api_core.core.domain.entities.database.filter import Filter
from nova_api_core.core.domain.entities.database.pagination import (
    PaginatedResult,
)
from nova_api_core.core.domain.entities.database.sort import Sort
from nova_api_core.infra.db.mongo.mongo_generic_crud import MongoGenericCRUD


@pytest_asyncio.fixture
async def mongo_db():
    client = AsyncMongoMockClient()
    db = client["test_db"]

    yield db

    client.close()


@pytest.fixture
def crud():
    return MongoGenericCRUD("users")


# =========================
# CREATE
# =========================
@pytest.mark.asyncio
async def test_create_single(mongo_db, crud):
    result = await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com", "age": 30},
    )

    assert result["_id"] is not None
    assert result["name"] == "John"
    assert result["email"] == "john@example.com"
    assert result["age"] == 30


@pytest.mark.asyncio
async def test_create_multiple(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com"},
    )
    await crud.create(
        mongo_db,
        data={"name": "Jane", "email": "jane@example.com"},
    )

    result = await crud.get(mongo_db)
    assert result.total == 2
    assert len(result.data) == 2


@pytest.mark.asyncio
async def test_create_without_id(mongo_db, crud):
    result = await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com"},
    )

    assert "_id" in result


# =========================
# GET BY ID
# =========================
@pytest.mark.asyncio
async def test_get_by_id(mongo_db, crud):
    created = await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com"},
    )

    result = await crud.get_by_id(mongo_db, created["_id"])

    assert result is not None
    assert result["_id"] == created["_id"]
    assert result["name"] == "John"


@pytest.mark.asyncio
async def test_get_by_id_with_string(mongo_db, crud):
    created = await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com"},
    )

    result = await crud.get_by_id(mongo_db, str(created["_id"]))

    assert result is not None
    assert result["name"] == "John"


@pytest.mark.asyncio
async def test_get_by_id_not_found(mongo_db, crud):
    fake_id = ObjectId()
    result = await crud.get_by_id(mongo_db, fake_id)
    assert result is None


@pytest.mark.asyncio
async def test_get_by_id_invalid_string(mongo_db, crud):
    result = await crud.get_by_id(mongo_db, "invalid_id")
    assert result is None


# =========================
# GET (PAGINATED)
# =========================
@pytest.mark.asyncio
async def test_get_all(mongo_db, crud):
    for i in range(3):
        await crud.create(
            mongo_db,
            data={"name": f"User{i}", "email": f"user{i}@example.com"},
        )

    result = await crud.get(mongo_db)

    assert isinstance(result, PaginatedResult)
    assert result.total == 3
    assert len(result.data) == 3


@pytest.mark.asyncio
async def test_get_with_skip_limit(mongo_db, crud):
    for i in range(10):
        await crud.create(
            mongo_db,
            data={"name": f"User{i}", "email": f"user{i}@example.com"},
        )

    result = await crud.get(mongo_db, skip=5, limit=3)

    assert result.total == 10
    assert len(result.data) == 3


@pytest.mark.asyncio
async def test_get_with_limit_exceeds_total(mongo_db, crud):
    for i in range(3):
        await crud.create(
            mongo_db,
            data={"name": f"User{i}", "email": f"user{i}@example.com"},
        )

    result = await crud.get(mongo_db, skip=0, limit=100)

    assert result.total == 3
    assert len(result.data) == 3


@pytest.mark.asyncio
async def test_get_empty(mongo_db, crud):
    result = await crud.get(mongo_db)

    assert result.total == 0
    assert len(result.data) == 0


# =========================
# GET WITH SORT
# =========================
@pytest.mark.asyncio
async def test_get_with_sort_ascending(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "Charlie", "email": "charlie@example.com", "age": 25},
    )
    await crud.create(
        mongo_db,
        data={"name": "Alice", "email": "alice@example.com", "age": 30},
    )
    await crud.create(
        mongo_db,
        data={"name": "Bob", "email": "bob@example.com", "age": 20},
    )

    result = await crud.get(mongo_db, sort=Sort(field="name", direction="asc"))

    assert len(result.data) == 3
    assert result.data[0]["name"] == "Alice"
    assert result.data[1]["name"] == "Bob"
    assert result.data[2]["name"] == "Charlie"


@pytest.mark.asyncio
async def test_get_with_sort_descending(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "Charlie", "email": "charlie@example.com", "age": 25},
    )
    await crud.create(
        mongo_db,
        data={"name": "Alice", "email": "alice@example.com", "age": 30},
    )
    await crud.create(
        mongo_db,
        data={"name": "Bob", "email": "bob@example.com", "age": 20},
    )

    result = await crud.get(mongo_db, sort=Sort(field="name", direction="desc"))

    assert len(result.data) == 3
    assert result.data[0]["name"] == "Charlie"
    assert result.data[1]["name"] == "Bob"
    assert result.data[2]["name"] == "Alice"


# =========================
# GET WITH FILTERS
# =========================
@pytest.mark.asyncio
async def test_get_with_filter_equals(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com"},
    )
    await crud.create(
        mongo_db,
        data={"name": "Jane", "email": "jane@example.com"},
    )

    result = await crud.get(
        mongo_db,
        filters=[Filter(field="name", operator="equals", value="John")],
    )

    assert result.total == 1
    assert len(result.data) == 1
    assert result.data[0]["name"] == "John"


@pytest.mark.asyncio
async def test_get_with_filter_not_equals(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com"},
    )
    await crud.create(
        mongo_db,
        data={"name": "Jane", "email": "jane@example.com"},
    )

    result = await crud.get(
        mongo_db,
        filters=[Filter(field="name", operator="not_equals", value="John")],
    )

    assert len(result.data) == 1
    assert result.data[0]["name"] == "Jane"


@pytest.mark.asyncio
async def test_get_with_filter_like(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "Johnny", "email": "johnny@example.com"},
    )
    await crud.create(
        mongo_db,
        data={"name": "Jane", "email": "jane@example.com"},
    )

    result = await crud.get(
        mongo_db,
        filters=[Filter(field="name", operator="like", value="John")],
    )

    assert len(result.data) == 1
    assert result.data[0]["name"] == "Johnny"


@pytest.mark.asyncio
async def test_get_with_filter_ilike(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "Johnny", "email": "johnny@example.com"},
    )
    await crud.create(
        mongo_db,
        data={"name": "JANE", "email": "jane@example.com"},
    )

    result = await crud.get(
        mongo_db,
        filters=[Filter(field="name", operator="ilike", value="jane")],
    )

    assert len(result.data) == 1
    assert result.data[0]["name"] == "JANE"


@pytest.mark.asyncio
async def test_get_with_filter_in(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com"},
    )
    await crud.create(
        mongo_db,
        data={"name": "Jane", "email": "jane@example.com"},
    )
    await crud.create(
        mongo_db,
        data={"name": "Bob", "email": "bob@example.com"},
    )

    result = await crud.get(
        mongo_db,
        filters=[
            Filter(field="name", operator="in", value=["John", "Jane"])
        ],
    )

    assert len(result.data) == 2


@pytest.mark.asyncio
async def test_get_with_filter_gt(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "User1", "email": "user1@example.com", "age": 20},
    )
    await crud.create(
        mongo_db,
        data={"name": "User2", "email": "user2@example.com", "age": 30},
    )
    await crud.create(
        mongo_db,
        data={"name": "User3", "email": "user3@example.com", "age": 25},
    )

    result = await crud.get(
        mongo_db,
        filters=[Filter(field="age", operator="gt", value=25)],
    )

    assert len(result.data) == 1
    assert result.data[0]["age"] == 30


@pytest.mark.asyncio
async def test_get_with_filter_gte(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "User1", "email": "user1@example.com", "age": 20},
    )
    await crud.create(
        mongo_db,
        data={"name": "User2", "email": "user2@example.com", "age": 30},
    )
    await crud.create(
        mongo_db,
        data={"name": "User3", "email": "user3@example.com", "age": 25},
    )

    result = await crud.get(
        mongo_db,
        filters=[Filter(field="age", operator="gte", value=25)],
    )

    assert len(result.data) == 2


@pytest.mark.asyncio
async def test_get_with_filter_lt(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "User1", "email": "user1@example.com", "age": 20},
    )
    await crud.create(
        mongo_db,
        data={"name": "User2", "email": "user2@example.com", "age": 30},
    )

    result = await crud.get(
        mongo_db,
        filters=[Filter(field="age", operator="lt", value=25)],
    )

    assert len(result.data) == 1
    assert result.data[0]["age"] == 20


@pytest.mark.asyncio
async def test_get_with_filter_lte(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "User1", "email": "user1@example.com", "age": 20},
    )
    await crud.create(
        mongo_db,
        data={"name": "User2", "email": "user2@example.com", "age": 30},
    )
    await crud.create(
        mongo_db,
        data={"name": "User3", "email": "user3@example.com", "age": 25},
    )

    result = await crud.get(
        mongo_db,
        filters=[Filter(field="age", operator="lte", value=25)],
    )

    assert len(result.data) == 2


@pytest.mark.asyncio
async def test_get_with_multiple_and_filters(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com", "age": 30},
    )
    await crud.create(
        mongo_db,
        data={"name": "Jane", "email": "jane@example.com", "age": 25},
    )
    await crud.create(
        mongo_db,
        data={"name": "Bob", "email": "bob@example.com", "age": 30},
    )

    result = await crud.get(
        mongo_db,
        filters=[
            Filter(field="name", operator="equals", value="John", db_operator="AND"),
            Filter(field="age", operator="equals", value=30, db_operator="AND"),
        ],
    )

    assert len(result.data) == 1
    assert result.data[0]["name"] == "John"


@pytest.mark.asyncio
async def test_get_with_or_filters(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com"},
    )
    await crud.create(
        mongo_db,
        data={"name": "Jane", "email": "jane@example.com"},
    )
    await crud.create(
        mongo_db,
        data={"name": "Bob", "email": "bob@example.com"},
    )

    result = await crud.get(
        mongo_db,
        filters=[
            Filter(field="name", operator="equals", value="John", db_operator="OR"),
            Filter(field="name", operator="equals", value="Jane", db_operator="OR"),
        ],
    )

    assert len(result.data) == 2


# =========================
# UPDATE
# =========================
@pytest.mark.asyncio
async def test_update(mongo_db, crud):
    created = await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com", "age": 30},
    )

    result = await crud.update(
        mongo_db,
        created["_id"],
        data={"name": "Jane", "age": 25},
    )

    assert result["_id"] == created["_id"]
    assert result["name"] == "Jane"
    assert result["age"] == 25
    assert result["email"] == "john@example.com"


@pytest.mark.asyncio
async def test_update_with_string_id(mongo_db, crud):
    created = await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com", "age": 30},
    )

    result = await crud.update(
        mongo_db,
        str(created["_id"]),
        data={"name": "Jane"},
    )

    assert result["name"] == "Jane"


@pytest.mark.asyncio
async def test_update_not_found(mongo_db, crud):
    fake_id = ObjectId()

    with pytest.raises(NotFoundException) as exc:
        await crud.update(
            mongo_db,
            fake_id,
            data={"name": "Jane"},
        )

    assert "Ressource introuvable" in exc.value.message


@pytest.mark.asyncio
async def test_update_partial(mongo_db, crud):
    created = await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com", "age": 30},
    )

    result = await crud.update(
        mongo_db,
        created["_id"],
        data={"name": "John Updated"},
    )

    assert result["name"] == "John Updated"
    assert result["email"] == "john@example.com"
    assert result["age"] == 30


# =========================
# DELETE
# =========================
@pytest.mark.asyncio
async def test_delete(mongo_db, crud):
    created = await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com"},
    )

    await crud.delete(mongo_db, created["_id"])

    result = await crud.get_by_id(mongo_db, created["_id"])
    assert result is None


@pytest.mark.asyncio
async def test_delete_with_string_id(mongo_db, crud):
    created = await crud.create(
        mongo_db,
        data={"name": "John", "email": "john@example.com"},
    )

    await crud.delete(mongo_db, str(created["_id"]))

    result = await crud.get_by_id(mongo_db, created["_id"])
    assert result is None


@pytest.mark.asyncio
async def test_delete_not_found(mongo_db, crud):
    fake_id = ObjectId()

    with pytest.raises(NotFoundException) as exc:
        await crud.delete(mongo_db, fake_id)

    assert "Ressource introuvable" in exc.value.message


@pytest.mark.asyncio
async def test_delete_invalid_string_id(mongo_db, crud):
    with pytest.raises(NotFoundException) as exc:
        await crud.delete(mongo_db, "invalid_id")

    assert "Ressource introuvable" in exc.value.message


@pytest.mark.asyncio
async def test_delete_multiple_and_verify(mongo_db, crud):
    await crud.create(
        mongo_db,
        data={"name": "User1", "email": "user1@example.com"},
    )
    await crud.create(
        mongo_db,
        data={"name": "User2", "email": "user2@example.com"},
    )

    result = await crud.get(mongo_db)
    assert result.total == 2

    user_id = result.data[0]["_id"]
    await crud.delete(mongo_db, user_id)

    result = await crud.get(mongo_db)
    assert result.total == 1


# =========================
# COMPLEX SCENARIOS
# =========================
@pytest.mark.asyncio
async def test_combined_filters_sort_pagination(mongo_db, crud):
    for i in range(20):
        await crud.create(
            mongo_db,
            data={
                "name": f"User{i}",
                "email": f"user{i}@example.com",
                "age": 20 + (i % 10),
            },
        )

    result = await crud.get(
        mongo_db,
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
# FIND RAW
# =========================
@pytest.mark.asyncio
async def test_find_raw(mongo_db, crud):

    await crud.create(
        mongo_db,
        data={
            "name": "John",
            "email": "john@example.com",
            "age": 30,
        },
    )

    result = await crud.find_raw(
        mongo_db,
        query={
            "age": {
                "$gte": 25,
            }
        },
    )

    assert len(result) == 1
    assert result[0]["name"] == "John"
    assert result[0]["email"] == "john@example.com"
    assert result[0]["age"] == 30


# =========================
# AGGREGATE RAW
# =========================
@pytest.mark.asyncio
async def test_aggregate_raw(mongo_db, crud):

    await crud.create(
        mongo_db,
        data={
            "name": "John",
            "email": "john@example.com",
            "age": 30,
            "country": "FR",
        },
    )

    await crud.create(
        mongo_db,
        data={
            "name": "Jane",
            "email": "jane@example.com",
            "age": 25,
            "country": "FR",
        },
    )

    result = await crud.aggregate_raw(
        mongo_db,
        pipeline=[
            {
                "$match": {
                    "country": "FR",
                }
            },
            {
                "$group": {
                    "_id": "$country",
                    "total": {
                        "$sum": 1,
                    },
                }
            },
        ],
    )

    assert len(result) == 1
    assert result[0]["_id"] == "FR"
    assert result[0]["total"] == 2
