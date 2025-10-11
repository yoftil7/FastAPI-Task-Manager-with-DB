import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.auth import create_access_token
from app import models


# ✅ Use shared in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///file::memory:?cache=shared"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Disable rate limiter for tests
app.dependency_overrides = {
    get_db: override_get_db,
}


@pytest.fixture(scope="function")
def client():
    # Fresh DB schema before each test
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def db():
    """Provide a direct database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def test_user(db):
    """Create a basic test user directly in DB."""
    user = models.User(
        username="tester",
        email="tester@example.com",
        hashed_password="$2b$12$zZxZc3c6fUQxA8RHZ6It3OqZo2CQAc9/Jg8Oe7dFEl9/d5hRj8eQS",  # bcrypt hash for "password"
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_header(test_user):
    """Return an Authorization header for test_user."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_user(db):
    user = models.User(
        username="admin_tester",
        email="admin@example.com",
        hashed_password="$2b$12$zZxZc3c6fUQxA8RHZ6It3OqZo2CQAc9/Jg8Oe7dFEl9/d5hRj8eQS",  # "password"
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_auth_header(admin_user):
    """Return Authorization header for admin user."""
    token = create_access_token(data={"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {token}"}
