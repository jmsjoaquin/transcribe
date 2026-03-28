from collections.abc import Generator
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.main import app
from app.models.user import User


@pytest.fixture
def fake_db():
    return object()


@pytest.fixture
def current_user() -> User:
    return User(
        id=1,
        email="tester@example.com",
        hashed_password="hashed",
        given_name="Test",
        last_name="User",
    )


@pytest.fixture
def client(fake_db, current_user) -> Generator[TestClient, None, None]:
    db = fake_db
    user = current_user

    def override_get_db():
        yield db

    def override_get_current_user() -> User:
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
