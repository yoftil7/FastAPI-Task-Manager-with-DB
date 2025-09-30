import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


# ✅ Use shared in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///file::memory:?cache=shared"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    # Fresh DB schema before each test
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def create_user(client):
    def _create_user(username="test", email="user@test.com", password="pass123"):
        resp = client.post(
            "/users", json={"username": username, "email": email, "password": password}
        )
        assert resp.status_code == 201
        return resp.json()

    return _create_user
