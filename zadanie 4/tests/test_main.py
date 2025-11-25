import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from database import Base, get_db
import models
import auth

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def admin_auth_headers(client: TestClient, db_session: TestingSessionLocal):
    admin_user = models.User(
        username="testadmin",
        hashed_password=auth.hash_password("adminpass"),
        roles="ROLE_ADMIN,ROLE_USER"
    )
    db_session.add(admin_user)
    db_session.commit()

    response = client.post("/login", data={"username": "testadmin", "password": "adminpass"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def regular_user_auth_headers(client: TestClient, db_session: TestingSessionLocal):
    user = models.User(
        username="testuser",
        hashed_password=auth.hash_password("userpass"),
        roles="ROLE_USER"
    )
    db_session.add(user)
    db_session.commit()

    response = client.post("/login", data={"username": "testuser", "password": "userpass"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_login_success(client: TestClient, regular_user_auth_headers):
    response = client.post("/login", data={"username": "testuser", "password": "userpass"})
    data = response.json()
    assert response.status_code == 200
    assert "access_token" in data


def test_login_failure_wrong_password(client: TestClient, regular_user_auth_headers):
    response = client.post("/login", data={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_get_user_details_success(client: TestClient, regular_user_auth_headers):
    response = client.get("/user_details", headers=regular_user_auth_headers)
    data = response.json()
    assert response.status_code == 200
    assert data["username"] == "testuser"
    assert data["roles"] == ["ROLE_USER"]


def test_get_user_details_no_token(client: TestClient):
    response = client.get("/user_details")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_create_user_success_by_admin(client: TestClient, admin_auth_headers):
    new_user_data = {"username": "newuser", "password": "newpassword123"}
    response = client.post("/users", json=new_user_data, headers=admin_auth_headers)
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"


def test_create_user_failure_by_regular_user(client: TestClient, regular_user_auth_headers):
    new_user_data = {"username": "anotheruser", "password": "password123"}
    response = client.post("/users", json=new_user_data, headers=regular_user_auth_headers)
    assert response.status_code == 403
    assert "Admin role required" in response.json()["detail"]