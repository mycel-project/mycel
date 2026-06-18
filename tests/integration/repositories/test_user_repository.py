import time

from src.repositories.user_repository import UserRepository


def test_user_create_and_get(db_fixture):
    repo = UserRepository(db=db_fixture)

    created = repo.create(
        name="Alice",
    )

    assert created.id is not None
    assert created.name == "Alice"
    assert created.conf is not None
    assert created.templates.root != {}

    fetched = repo.get(created.id)
    
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "Alice"
    assert fetched.templates.root != {}    


def test_user_update(db_fixture):
    repo = UserRepository(db=db_fixture)
    
    created = repo.create(
        name="Bob Old",
    )

    created.name = "Bob New"
    
    repo.update(created)

    updated = repo.get(created.id)

    assert updated is not None
    assert updated.id == created.id
    assert updated.name == "Bob New"


def test_user_delete(db_fixture):
    repo = UserRepository(db=db_fixture)
    
    created = repo.create(
        name="Charlie To Delete",
    )

    repo.delete(created.id)

    fetched = repo.get(created.id)
    assert fetched is None


def test_user_list_ordering(db_fixture):
    repo = UserRepository(db=db_fixture)
        
    u1 = repo.create(name="Dave")
    time.sleep(0.002) 
    u2 = repo.create(name="Eve")
    time.sleep(0.002)
    u3 = repo.create(name="Frank")
    
    results = repo.list()

    assert len(results) >= 3 # default user could be created so >=
    
    assert results[-3].id == u1.id
    assert results[-2].id == u2.id
    assert results[-1].id == u3.id


def test_pending_node(db_fixture):
    repo = UserRepository(db=db_fixture)
    user = repo.create(name="Test")
    
    assert repo.get_pending_review_id(user.id) is None
    
    repo.set_pending_review_id(user.id, "some-node-uuid")
    assert repo.get_pending_review_id(user.id) == "some-node-uuid"
    
    repo.set_pending_review_id(user.id, None)
    assert repo.get_pending_review_id(user.id) is None
