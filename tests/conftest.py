"""Shared pytest fixtures: an isolated in-memory database and a test client."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app


@pytest.fixture()
def db_session():
    """Provide a fresh in-memory SQLite database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestingSessionLocal
    app.dependency_overrides.clear()


@pytest.fixture()
def client(db_session):
    """A FastAPI TestClient wired to the isolated in-memory database."""
    return TestClient(app)


@pytest.fixture()
def make_citizen(client):
    """Factory fixture: sign up a citizen via the real API and return (token, user)."""

    def _make(phone: str = "9000000001", password: str = "secret123", full_name: str = "Test Citizen", preferred_language: str = "en"):
        response = client.post(
            "/auth/signup",
            json={
                "full_name": full_name,
                "phone": phone,
                "password": password,
                "preferred_language": preferred_language,
            },
        )
        assert response.status_code == 200, response.text
        body = response.json()
        return body["access_token"], body["user"]

    return _make


@pytest.fixture()
def make_admin(db_session):
    """Factory fixture: seed an admin account directly into the DB (as a real deployment would)."""
    from backend.models import User
    from backend.services.auth_service import hash_password

    def _make(phone: str = "9999999999", password: str = "adminpass", full_name: str = "Test Admin"):
        db = db_session()
        user = User(
            full_name=full_name,
            phone=phone,
            password_hash=hash_password(password),
            role="admin",
            preferred_language="en",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        return user

    return _make


@pytest.fixture()
def make_worker(client, make_admin):
    """Factory fixture: seed an admin, then use it to create a worker via the real API."""

    def _make(phone: str = "9000000002", password: str = "secret123", full_name: str = "Test Worker", ward: str = "Ward 14", preferred_language: str = "hi"):
        # Uses its own dedicated bootstrap-admin phone so this fixture composes safely
        # with a test that also calls make_admin() directly with the default phone.
        bootstrap_admin_phone = "9999900000"
        make_admin(phone=bootstrap_admin_phone, password="bootstrap-pass")
        admin_login = client.post("/auth/login", json={"phone": bootstrap_admin_phone, "password": "bootstrap-pass"})
        admin_token = admin_login.json()["access_token"]

        response = client.post(
            "/admin/workers",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "full_name": full_name,
                "phone": phone,
                "password": password,
                "ward": ward,
                "preferred_language": preferred_language,
            },
        )
        assert response.status_code == 200, response.text

        worker_login = client.post("/auth/login", json={"phone": phone, "password": password})
        body = worker_login.json()
        return body["access_token"], body["user"]

    return _make
