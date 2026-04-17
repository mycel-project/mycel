from src.db import Db
from pathlib import Path
import pytest

from src.repositories.collection_repository import CollectionRepository
from src.services.collection_service import CollectionService

@pytest.fixture
def db():
    return Db(Path("file::memory:?cache=shared"))

@pytest.fixture
def col(db):
    service = CollectionService(db)

    col = service.create_collection("test")

    return col  
