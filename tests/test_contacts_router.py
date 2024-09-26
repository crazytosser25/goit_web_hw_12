from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app_main import app
from src.contacts.schemas import ContactCreation, ContactScema
from src.auth.schemas import UserDb
from src.database import Base, get_db
from unittest.mock import patch
from fastapi_limiter.depends import RateLimiter


@pytest.fixture(autouse=True)
def disable_rate_limiter():
    with patch.object(RateLimiter, "__call__", return_value=None):
        yield


# Set up SQLite for testing
DATABASE_URL = "sqlite:///test.db"
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a new FastAPI TestClient
client = TestClient(app)


@pytest.fixture(scope="module")
def session():
    """Set up the database for testing with SQLite."""
    Base.metadata.drop_all(bind=engine)  # Drop any existing tables
    Base.metadata.create_all(bind=engine)  # Create fresh tables
    db = TestingSessionLocal()
    try:
        yield db  # Provide the session to tests
    finally:
        db.close()


@pytest.fixture(scope="module")
def override_get_db(session):
    """Override the get_db dependency to use the testing session."""
    def _get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _get_db  # Override the FastAPI dependency
    yield
    app.dependency_overrides.clear()  # Clean up overrides after tests


@pytest.fixture(scope="module")
def mock_user():
    """Fixture for creating a mock authenticated user."""
    return UserDb(
        id=1,
        username='user1',
        email='user1@google.com',
        created_at=datetime.now(),
        confirmed=True,
        avatar=None
    )


@patch('src.contacts.crud.CrudOps.create_contact')
@patch('src.auth.auth.auth_service.get_current_user', return_value=mock_user)
# @patch('src.auth.auth.auth_service')
def test_create_contact(mock_get_current_user, mock_create_contact, override_get_db, mock_user):
    """Test creating a contact."""
    mock_get_current_user.return_value = mock_user

    # Mocking the creation of a contact
    mock_contact_data = ContactCreation(
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        phone_number="1234567890",
        birthday=datetime.now().date().isoformat(),
        other_info="Some additional information"
    )

    mock_create_contact.return_value = ContactScema(
        id=1,
        **mock_contact_data.model_dump()
    )

    response = client.post("/api/contacts/", json=mock_contact_data.model_dump())

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        **mock_contact_data.model_dump()
    }


@patch('src.contacts.crud.CrudOps.get_all_contacts')
@patch('src.auth.auth.auth_service.get_current_user', return_value=mock_user)
# @patch('src.auth.auth.auth_service')
def test_read_contacts(mock_get_current_user, mock_get_all_contacts, override_get_db, mock_user):
    """Test reading contacts."""
    mock_get_current_user.return_value = mock_user

    mock_contacts = [
        ContactScema(
            id=1,
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            phone_number="1234567890",
            birthday=datetime.now().date().isoformat(),
            other_info="Some additional information"
        ),
        ContactScema(
            id=2,
            first_name="John",
            last_name="Smith",
            email="john.smith@example.com",
            phone_number="0987654321",
            birthday=datetime.now().date().isoformat(),
            other_info="Some additional information"
        )
    ]

    mock_get_all_contacts.return_value = mock_contacts

    response = client.get("/api/contacts/")

    assert response.status_code == 200
    assert response.json() == [contact.model_dump() for contact in mock_contacts]
