
import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.engine import make_url

# Safety guard: the application creates tables during import.
# Never let these tests run against a development database.
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL is required for registration tests")

url = make_url(database_url)
if url.database != "unify_auth_pytest" or url.host != "unify-auth-test-db":
    raise RuntimeError("Registration tests require the isolated pytest database")

from app.database import SessionLocal
from app.main import app
from app.models import User


@pytest.fixture
def test_email():
    email = f"registration-{uuid4().hex}@example.com"
    yield email

    # Cleanup runs even when an assertion fails.
    with SessionLocal() as db:
        db.execute(delete(User).where(User.email == email))
        db.commit()


@pytest.mark.parametrize("role", ["admin", "organizer"])
def test_public_registration_rejects_privileged_roles(role, test_email):
    payload = {
        "email": test_email,
        "display_name": "Security Test",
        "password": "TestOnly-Pass123!",
        "role": role,
    }

    with TestClient(app) as client:
        response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 422

    # Rejection must not create an account.
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == test_email))
        assert user is None


@pytest.mark.parametrize("explicit_role", [False, True])
def test_public_registration_creates_student(explicit_role, test_email):
    payload = {
        "email": test_email,
        "display_name": "Student Test",
        "password": "TestOnly-Pass123!",
    }

    if explicit_role:
        payload["role"] = "student"

    with TestClient(app) as client:
        response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 201
    assert response.json()["role"] == "student"

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == test_email))
        assert user is not None
        assert user.role.value == "student"
