import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
from app.models.user import User

# Setup test database
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

def test_register(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "newpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["username"] == "newuser"
    assert "id" in data

def test_login(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["email"],
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["email"],
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_register_duplicate_email(client, test_user):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",  # Same email as test_user
            "username": "different_user",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_register_duplicate_username(client, test_user):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "different@example.com",
            "username": "testuser",  # Same username as test_user
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]

def test_login_invalid_email(client):
    response = client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 401

def test_register_invalid_data(client):
    """Test registration with invalid data"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "invalid-email",  # Invalid email format
            "username": "user",
            "password": "pass"
        }
    )
    assert response.status_code == 422  # Validation error

def test_register_database_error(client, monkeypatch):
    """Test registration with database error"""
    from sqlalchemy.exc import SQLAlchemyError
    
    def mock_commit(*args, **kwargs):
        raise SQLAlchemyError("Database error")
    
    from sqlalchemy.orm import Session
    monkeypatch.setattr(Session, "commit", mock_commit)
    
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "Database error" in response.json()["detail"] 