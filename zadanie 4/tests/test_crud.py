import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from database import get_db
import models

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
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
    models.Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    models.Base.metadata.drop_all(bind=engine)

def test_create_movie(client):
    response = client.post("/movies", json={"title": "Test Movie", "genres": "Action"})
    assert response.status_code == 201
    assert response.json()["title"] == "Test Movie"

def test_read_movie_not_found(client):
    response = client.get("/movies/999")
    assert response.status_code == 404

def test_update_movie(client):
    res = client.post("/movies", json={"title": "Old", "genres": "Old"})
    mid = res.json()["id"]
    res = client.put(f"/movies/{mid}", json={"title": "New", "genres": "New"})
    assert res.status_code == 200
    assert res.json()["title"] == "New"

def test_delete_movie(client):
    res = client.post("/movies", json={"title": "To Delete", "genres": "None"})
    mid = res.json()["id"]
    res = client.delete(f"/movies/{mid}")
    assert res.status_code == 204
    res = client.get(f"/movies/{mid}")
    assert res.status_code == 404

def test_create_tag(client):
    response = client.post("/tags", json={"user_id": 1, "movie_id": 1, "tag": "funny", "timestamp": 123})
    assert response.status_code == 201
    assert response.json()["tag"] == "funny"

def test_read_tags_list(client):
    client.post("/tags", json={"user_id": 1, "movie_id": 1, "tag": "A", "timestamp": 1})
    client.post("/tags", json={"user_id": 2, "movie_id": 2, "tag": "B", "timestamp": 2})
    response = client.get("/tags")
    assert len(response.json()) == 2