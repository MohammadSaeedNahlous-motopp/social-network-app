import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from db.database import get_db
from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    db: Session = next(get_db())
    try:
        yield db
    finally:
        db.close()