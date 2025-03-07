import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


from app.main import app
from app.db.database import Base, get_db
from app.models.user import User

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create TestingSessionLocal
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after all tests are done
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(client, test_db):
    # Clean up any existing user first
    test_db.query(User).filter(
        (User.email == "test@example.com") | 
        (User.username == "testuser")
    ).delete()
    test_db.commit()
    
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    }
    
    response = client.post("/api/auth/register", json=user_data)
    if response.status_code == 400:
        print("Registration error:", response.json())
    assert response.status_code == 200, f"Registration failed: {response.json()}"
    return response.json()

@pytest.fixture(scope="function")
def test_user_token(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={"username": test_user["email"], "password": "testpassword"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["TESTING"] = "True"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["ALGORITHM"] = "HS256"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    yield