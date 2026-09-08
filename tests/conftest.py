import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from auth.oauth2 import get_current_user
from db.database import Base, get_db
from db.hash import Hash
from db.group_role import get_role_obj
from db.seed import seed_group_roles
from main import app
from models.enums import GroupRole
from models.user import DBUser
from models.group import DBGroup
from models.group_member import DBGroupMember
from models.group_role import DBGroupRole

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
        seed_group_roles(db)
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
        existing_user = db.query(DBUser).filter(DBUser.email == email).first()

        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists.")

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


@pytest.fixture
def create_test_group(db: Session, create_test_user):
    def _create_test_group(
        owner,
        name="Python Developers",
        description="A group for Python developers",
        background_img=None,
        profile_img=None,
        is_public=True,
    ):
        if owner is None:
            owner = create_test_user()

        group = DBGroup(
            name=name,
            description=description,
            owner_id=owner.id,
            background_img=background_img,
            profile_img=profile_img,
            is_public=is_public,
        )

        db.add(group)
        db.commit()
        db.refresh(group)

        return group

    return _create_test_group


@pytest.fixture
def create_test_group_member(db: Session):
    def _create_test_group_member(
        group: DBGroup,
        user: DBUser,
        role: GroupRole = GroupRole.member,
    ):
        membership = DBGroupMember(
            group_id=group.id,
            user_id=user.id,
            role=role,
        )

        db.add(membership)
        db.commit()
        db.refresh(membership)

        return membership

    return _create_test_group_member


@pytest.fixture
def get_test_group_role(db: Session):
    def _get_test_group_role(role: GroupRole):
        return get_role_obj(db=db, role=role)


    return _get_test_group_role
