import time

from src.models.collection_conf import CollectionConf
from src.models.fsrs_conf import FsrsConf
from src.repositories.collection_repository import CollectionRepository

def test_collection_create_and_get(db_fixture, default_user):
    repo = CollectionRepository(db=db_fixture)
    conf = CollectionConf()
    fsrsconf = FsrsConf()

    created = repo.create(
        user_id=default_user,
        name="Deck",
        conf=conf,
        fsrsconf=fsrsconf
    )

    assert created.id is not None
    assert created.name == "Deck"

    fetched = repo.get(created.id)
    
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
        fsrsconf=FsrsConf()
    )
    
    created.name = "New Name"
    repo.update(created)
    
    updated = repo.get(created.id)
    assert updated is not None
    assert updated.name == "New Name"
    assert updated.conf is not None
    assert updated.fsrsconf is not None
    
def test_collection_delete(db_fixture, default_user):
    repo = CollectionRepository(db=db_fixture)
    conf = CollectionConf()
    fsrsconf = FsrsConf()
    
    created = repo.create(user_id=default_user, name="To Delete", conf=conf, fsrsconf=fsrsconf)

    repo.delete(created.id)

    fetched = repo.get(created.id)
    assert fetched is None

def test_collection_list_ordering(db_fixture, default_user):
    repo = CollectionRepository(db=db_fixture)
    
    c1 = repo.create(user_id=default_user, name="Collection 1", conf=CollectionConf(), fsrsconf=FsrsConf())
    time.sleep(0.002) 
    c2 = repo.create(user_id=default_user, name="Collection 2", conf=CollectionConf(), fsrsconf=FsrsConf())
    time.sleep(0.002)
    c3 = repo.create(user_id=default_user, name="Collection 3", conf=CollectionConf(), fsrsconf=FsrsConf())
    
    results = repo.list(default_user)

    assert len(results) == 3
    assert results[0].id == c1.id
    assert results[1].id == c2.id
    assert results[2].id == c3.id
