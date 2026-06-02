import time

from src.models.user_conf import UserConf
from src.repositories.user_repository import UserRepository


def test_user_create_and_get(db_fixture):
    repo = UserRepository(db=db_fixture)
    conf = UserConf()

    created = repo.create(
        name="Alice",
        conf=conf
    )

    assert created.id is not None
    assert created.name == "Alice"
    assert created.conf is not None

    fetched = repo.get(created.id)
    
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "Alice"


def test_user_update(db_fixture):
    repo = UserRepository(db=db_fixture)
    conf = UserConf()
    
    created = repo.create(
        name="Bob Old",
        conf=conf
    )

    created.name = "Bob New"
    
    repo.update(created)

    updated = repo.get(created.id)

    assert updated is not None
    assert updated.id == created.id
    assert updated.name == "Bob New"


def test_user_delete(db_fixture):
    repo = UserRepository(db=db_fixture)
    conf = UserConf()
    
    created = repo.create(
        name="Charlie To Delete",
        conf=conf
    )

    repo.delete(created.id)

    fetched = repo.get(created.id)
    assert fetched is None


def test_user_list_ordering(db_fixture):
    repo = UserRepository(db=db_fixture)
        
    u1 = repo.create(name="Dave", conf=UserConf())
    time.sleep(0.002) 
    u2 = repo.create(name="Eve", conf=UserConf())
    time.sleep(0.002)
    u3 = repo.create(name="Frank", conf=UserConf())
    
    results = repo.list()

    assert len(results) >= 3 # default user could be created so >=
    
    assert results[-3].id == u1.id
    assert results[-2].id == u2.id
    assert results[-1].id == u3.id
