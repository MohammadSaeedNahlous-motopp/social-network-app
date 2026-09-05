import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from auth.oauth2 import get_current_user
from db.database import Base, get_db
from db.hash import Hash
from main import app
from models.user import DBUser
from models.group import DBGroup

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)

    db: Session = TestingSessionLocal()

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
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def create_test_user(db: Session):
    def _create_test_user(email="test_user@example.com", name="John Doe"):
        user = DBUser(
            name=name,
            email=email,
            password=Hash.hash("password123"),
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    return _create_test_user


@pytest.fixture
def authenticated_user(create_test_user):
    def _authenticated_user(
        email="test_user@example.com",
        name="John Doe",
    ):
        user = create_test_user(email=email, name=name)

        app.dependency_overrides[get_current_user] = lambda: user

        return user

    yield _authenticated_user

    app.dependency_overrides.pop(get_current_user, None)
