import asyncio
from pathlib import Path
import pytest

from src.main import Application


@pytest.fixture(scope="session")
def app():    
    db_path = "pytest.db"
    app = Application(db_path=str(db_path))
    
    asyncio.run(app.init_async())
    return app

@pytest.fixture(autouse=True)
def clean_db(app):
    yield
    app.db.clear_all()

@pytest.fixture()
def col_service(app):
    return app.services["collection_service"]

@pytest.fixture()
def user_service(app):
    return app.services["user_service"]

@pytest.fixture
def user(user_service):
    user_id = 1
    try:
        user = user_service.get_user(user_id)
    except:
        user = user_service.create_user(id=user_id, name="TestUser")
    return user.id

@pytest.fixture
def col(col_service, user):
    col_id = 102020102
    try:
        col = col_service.get_collection(col_id)
    except:
        col = col_service.create_collection(user_id=user, name="TestCol", id=col_id)
    return col.id
