import time

from src.models.collection_conf import CollectionConf
from src.models.algo_conf import AlgoConf
from src.repositories.collection_repository import CollectionRepository

def test_collection_create_and_get(db_fixture, default_user):
    repo = CollectionRepository(db=db_fixture)
    conf = CollectionConf()
    algoconf = AlgoConf()

    created = repo.create(
        user_id=default_user,
        name="Deck",
        conf=conf,
        algoconf=algoconf
    )

    assert created.id is not None
    assert created.name == "Deck"

    fetched = repo.get(default_user, created.id)
    
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "Deck"
    assert fetched.user_id == default_user

def test_collection_partial_update(db_fixture, default_user):
    repo = CollectionRepository(db=db_fixture)
    
    created = repo.create(
        user_id=default_user,
        name="Old Name",
        conf=CollectionConf(),
        algoconf=AlgoConf()
    )
    
    created.name = "New Name"
    repo.update(default_user, created)
    
    updated = repo.get(default_user, created.id)
    assert updated is not None
    assert updated.name == "New Name"
    assert updated.conf is not None
    assert updated.algoconf is not None
    
def test_collection_delete(db_fixture, default_user):
    repo = CollectionRepository(db=db_fixture)
    conf = CollectionConf()
    algoconf = AlgoConf()
    
    created = repo.create(user_id=default_user, name="To Delete", conf=conf, algoconf=algoconf)

    repo.delete(default_user, created.id)

    fetched = repo.get(default_user, created.id)
    assert fetched is None

def test_collection_list_ordering(db_fixture, default_user):
    repo = CollectionRepository(db=db_fixture)
    
    c1 = repo.create(user_id=default_user, name="Collection 1", conf=CollectionConf(), algoconf=AlgoConf())
    time.sleep(0.002) 
    c2 = repo.create(user_id=default_user, name="Collection 2", conf=CollectionConf(), algoconf=AlgoConf())
    time.sleep(0.002)
    c3 = repo.create(user_id=default_user, name="Collection 3", conf=CollectionConf(), algoconf=AlgoConf())
    
    results = repo.list(default_user)

    assert len(results) == 3
    assert results[0].id == c1.id
    assert results[1].id == c2.id
    assert results[2].id == c3.id
