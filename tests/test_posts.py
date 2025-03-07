import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db

# Setup test database (same as in test_auth.py)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Helper function to create a user and get token
def get_user_token():
    # Register a user
    client.post(
        "/api/auth/register",
        json={"email": "post_test@example.com", "username": "postuser", "password": "password123"}
    )
    
    # Login to get token
    response = client.post(
        "/api/auth/login",
        data={"username": "post_test@example.com", "password": "password123"}
    )
    return response.json()["access_token"]

def test_create_post():
    token = get_user_token()
    response = client.post(
        "/api/posts/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Post", "content": "This is a test post content"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "This is a test post content"
    assert "id" in data

def test_read_posts():
    response = client.get("/api/posts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_update_post():
    # First create a post
    token = get_user_token()
    post_response = client.post(
        "/api/posts/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Post to Update", "content": "Original content"}
    )
    post_id = post_response.json()["id"]
    
    # Then update it
    update_response = client.put(
        f"/api/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Updated Post", "content": "Updated content"}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated Post"
    assert data["content"] == "Updated content"

def test_delete_post():
    # First create a post
    token = get_user_token()
    post_response = client.post(
        "/api/posts/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Post to Delete", "content": "Content to delete"}
    )
    post_id = post_response.json()["id"]
    
    # Then delete it
    delete_response = client.delete(
        f"/api/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/posts/{post_id}")
    assert get_response.status_code == 404 