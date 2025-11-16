import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

# 테스트용 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "CryptoWatcher Bot API" in response.json()["message"]


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_user(client):
    user_data = {
        "telegram_chat_id": "123456789",
        "base_currency": "USD"
    }
    response = client.post("/api/users", json=user_data)
    assert response.status_code == 200
    assert response.json()["telegram_chat_id"] == "123456789"
    assert response.json()["base_currency"] == "USD"


def test_create_duplicate_user(client):
    user_data = {
        "telegram_chat_id": "123456789",
        "base_currency": "USD"
    }
    client.post("/api/users", json=user_data)
    response = client.post("/api/users", json=user_data)
    assert response.status_code == 400


def test_get_user(client):
    user_data = {
        "telegram_chat_id": "123456789",
        "base_currency": "USD"
    }
    client.post("/api/users", json=user_data)
    response = client.get("/api/users/123456789")
    assert response.status_code == 200
    assert response.json()["telegram_chat_id"] == "123456789"


def test_get_nonexistent_user(client):
    response = client.get("/api/users/999999999")
    assert response.status_code == 404

