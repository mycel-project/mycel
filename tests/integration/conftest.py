import time
import asyncio
import os
import tempfile
import pytest
from uuid import uuid4
import jwt

from src.main import Application
from src.repositories.import_export_repository import ImportExportRepository
from src.repositories.node_repository import NodeRepository
from src.repositories.review_repository import ReviewRepository
from src.types.node_type import NodeType

def generate_token(user_id: str, expires_in_seconds: int = 3600) -> str:
    secret_key_test = "test_key"
    now = int(time.time())
    
    payload = {
        "iss": "my-app-auth",
        "sub": user_id,
        "aud": "authenticated",
        "exp": now + expires_in_seconds,
        "iat": now,
        "role": "authenticated",
    }
    
    token = jwt.encode(payload, secret_key_test, algorithm="HS256")
    return token

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

@pytest.fixture
def api(client):
    class Api:
        def get(self, url, token, headers=None, **kwargs):
            auth_headers = {"Authorization": f"Bearer {token}"}
            if headers:
                auth_headers.update(headers)
            return client.get(url, headers=auth_headers, **kwargs)

        def post(self, url, token=None, body=None, headers=None, **kwargs):
            auth_headers = {"Authorization": f"Bearer {token}"}
            if headers:
                auth_headers.update(headers)
            return client.post(url, json=body, headers=auth_headers, **kwargs)

        def patch(self, url, token, body=None, headers=None, **kwargs):
            auth_headers = {"Authorization": f"Bearer {token}"}
            if headers:
                auth_headers.update(headers)
            return client.patch(url, json=body, headers=auth_headers, **kwargs)

        def delete(self, url, token, headers=None, **kwargs):
            auth_headers = {"Authorization": f"Bearer {token}"}
            if headers:
                auth_headers.update(headers)
            return client.delete(url, headers=auth_headers, **kwargs)

    return Api()

@pytest.fixture(autouse=True)
def clean_db(app):
    app.db.clear_all()
    # Recreate default user after clearing
    from src.db import DEFAULT_USER_ID
    import time
    import json
    app.db.execute(
        "INSERT INTO users (id, name, created_at, conf) VALUES (:id, :name, :now, :conf)",
        {"id": DEFAULT_USER_ID, "name": "default", "now": int(time.time() * 1000), "conf": json.dumps({})}
    )
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
    """
    Generate a different user with a valid token at each call
    """
    def _create_user(id: str | None = None, name: str = "TestUser"):
        if id is None:
            id = str(uuid4())
        token = generate_token(id)
        return user_service.create_user(id=id, name=name), token
    return _create_user

@pytest.fixture
def create_col(col_service):
    def _create_col(name: str = "TestCol", user_id: str | None = None):
        if user_id is None:
            user_id = str(uuid4())
        return col_service.create_collection(user_id=user_id, name=name)
    return _create_col

@pytest.fixture()
def node_service(app):
    return app.services["node_service"]

@pytest.fixture()
def create_node_use_case(app):
    return app.create_node_usecase

@pytest.fixture
def create_node(create_node_use_case):
    def _create_node(col_id, user_id, type=NodeType.FRAGMENT, content="Test content", parent_id=None, position=None):
        return create_node_use_case.execute(
            user_id=user_id,
            collection_id=col_id,
            type=type,
            content=content,
            parent_id=parent_id,
            position=position,
        )
    return _create_node

@pytest.fixture
def priority_service(app):
    return app.services["priority_service"]

@pytest.fixture
def node_repo(app) -> NodeRepository:
    return NodeRepository(db=app.db)

@pytest.fixture
def import_export_repo(app):
    return ImportExportRepository(db=app.db)

@pytest.fixture
def default_collection(app, default_user, generate_id):
    col_id = generate_id()
    app.db.execute(
        "INSERT INTO collections (id, user_id, name, created_at, updated_at, conf, algoconf) VALUES (:id, :user_id, 'Test', 0, 0, '{}', '{}')",
        {"id": col_id, "user_id": default_user}
    )
    return col_id

@pytest.fixture
def review_repo(app) -> ReviewRepository:
    return ReviewRepository(db=app.db)
