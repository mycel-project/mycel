import time

from uuid import uuid4
from src.repositories.idempotency_repository import IdempotencyRepository


def test_idempotency_set_and_get(db_fixture):
    repo = IdempotencyRepository(db=db_fixture)
    user_id = str(uuid4())
    key = str(uuid4())
    body = {"data": {"id": "123", "name": "test"}}

    repo.set(user_id, key, body)
    result = repo.get(user_id, key)

    assert result == body

def test_idempotency_key_not_found(db_fixture):
    repo = IdempotencyRepository(db=db_fixture)
    result = repo.get(str(uuid4()), str(uuid4()))
    assert result is None

def test_idempotency_different_users_same_key(db_fixture):
    repo = IdempotencyRepository(db=db_fixture)
    key = str(uuid4())
    body1 = {"data": {"id": "1"}}
    body2 = {"data": {"id": "2"}}

    repo.set("user-1", key, body1)
    repo.set("user-2", key, body2)

    assert repo.get("user-1", key) == body1
    assert repo.get("user-2", key) == body2

def test_idempotency_purge_expired(db_fixture):
    repo = IdempotencyRepository(db=db_fixture)
    user_id = str(uuid4())
    key = str(uuid4())
    body = {"data": {"id": "123"}}

    repo.set(user_id, key, body)
    repo.purge_expired(int(time.time() * 1000) + 1)

    assert repo.get(user_id, key) is None
