import asyncio
import os
import tempfile
import pytest

from src.main import Application


@pytest.fixture(scope="session")
def app():
    db_url = os.getenv("TEST_DATABASE_URL")  # ex: postgresql://user:pass@localhost/testdb
    
    if db_url:
        app = Application(db_path=db_url)
    else:
        with tempfile.NamedTemporaryFile(suffix="test.db", delete=False) as f:
            app = Application(db_path=f.name)
                
    asyncio.run(app.init_async())
    return app

@pytest.fixture(autouse=True)
def clean_db(app):
    app.db.clear_all()
    yield
    app.db.clear_all()

@pytest.fixture()
def col_service(app):
    return app.services["collection_service"]

@pytest.fixture()
def user_service(app):
    return app.services["user_service"]

@pytest.fixture
def create_user(user_service):
    def _create_user(id=1, name="TestUser"):
        return user_service.create_user(id=id, name=name)
    return _create_user

@pytest.fixture
def create_col(col_service):
    def _create_col(name="TestCol", user_id=1):
        return col_service.create_collection(user_id=user_id, name=name)
    return _create_col
