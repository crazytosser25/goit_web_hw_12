import unittest
from datetime import datetime, date, timedelta
from pydantic import ValidationError
from unittest.mock import MagicMock, patch, ANY
from sqlalchemy.orm import Session

from src.auth.schemas import UserDb
from src.contacts import models, schemas
from src.contacts.crud import CrudOps


class TestCrudContacts(unittest.TestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = UserDb(
            id=1,
            username='user1',
            email='user1@google.com',
            created_at=datetime.now(),
            confirmed=True,
            avatar=None
        )

    @patch('src.contacts.models.Contact')
    def test_create_contact(self, MockContact):
        # Prepare test data
        contact_data = schemas.ContactCreation(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            birthday="1985-06-15",
            other_info="Friend from work"
        )

        # Set up mock for the new contact that will be created
        mock_contact_instance = MockContact.return_value
        mock_contact_instance.id = 1
        # Call the method being tested
        result = CrudOps.create_contact(self.session, contact_data, self.user)
        # Assertions
        # Ensure a new contact is created with the correct data
        MockContact.assert_called_once_with(**contact_data.model_dump(), user_id=self.user.id)
        # Ensure the contact is added to the session
        self.session.add.assert_called_once_with(mock_contact_instance)
        # Ensure the session commit and refresh are called
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(mock_contact_instance)
        # Ensure the method returns the created contact
        self.assertEqual(result, mock_contact_instance)

    @patch('src.contacts.models.Contact')  # Mock the Contact model
    def test_get_contact_found(self, MockContact):
        # Prepare test data
        contact_id = 1
        # Set up the mock query chain (query -> filter -> first)
        mock_query = self.session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = MockContact  # Simulate finding a contact
        # Call the method being tested
        result = CrudOps.get_contact(self.session, contact_id, self.user)
        # Assertions
        # Ensure query is called on the Contact model
        self.session.query.assert_called_once_with(models.Contact)
        # Ensure filter is applied with the correct arguments (user_id and contact id)
        mock_query.filter.assert_called_once_with(
            ANY,  # Allow any BinaryExpression for user_id
            ANY  # Allow any BinaryExpression for contact id
        )
        # Ensure first() is called to retrieve the contact
        mock_filter.first.assert_called_once()
        # Ensure the method returns the found contact
        self.assertEqual(result, MockContact)

    def test_get_contact_not_found(self):
        # Prepare test data
        contact_id = 1
        # Set up the mock query chain to return None (contact not found)
        mock_query = self.session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None  # Simulate contact not found
        # Call the method being tested
        result = CrudOps.get_contact(self.session, contact_id, self.user)
        # Assertions
        # Ensure query is called on the Contact model
        self.session.query.assert_called_once_with(models.Contact)
        # Ensure filter is applied with the correct arguments (user_id and contact id)
        mock_query.filter.assert_called_once_with(
            ANY,  # Allow any BinaryExpression for user_id
            ANY  # Allow any BinaryExpression for contact id
        )
        # Ensure first() is called to retrieve the contact
        mock_filter.first.assert_called_once()
        # Ensure the method returns None when no contact is found
        self.assertIsNone(result)

    @patch('src.contacts.models.Contact')  # Mock the Contact model
    def test_get_all_contacts(self, MockContact):
        # Prepare mock data - a list of contact instances
        mock_contacts = [MockContact(), MockContact()]
        # Set up the mock query chain (query -> filter -> all)
        mock_query = self.session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.all.return_value = mock_contacts  # Simulate a list of contacts
        # Call the method being tested
        result = CrudOps.get_all_contacts(self.session, self.user)
        # Assertions
        # Ensure query is called on the Contact model
        self.session.query.assert_called_once_with(models.Contact)
        # Ensure filter is applied with the correct argument (user_id)
        mock_query.filter.assert_called_once_with(
            models.Contact.user_id == self.user.id
        )
        # Ensure all() is called to retrieve the list of contacts
        mock_filter.all.assert_called_once()
        # Ensure the method returns the list of contacts
        self.assertEqual(result, mock_contacts)

    @patch('src.contacts.models.Contact')  # Mock the Contact model
    @patch('src.contacts.crud.Session')  # Mock the database session
    def test_upcoming_birthdays_with_contacts(self, MockSession, MockContact):
        """Test case when contacts have upcoming birthdays."""
        # Create mock contacts with birthdays in the next 7 days
        mock_contact1 = MagicMock()
        mock_contact1.first_name = "John"
        mock_contact1.last_name = "Smith"
        mock_contact1.birthday = date.today() + timedelta(days=3)

        mock_contact2 = MagicMock()
        mock_contact2.first_name = "Jane"
        mock_contact2.last_name = "Doe"
        mock_contact2.birthday = date.today() + timedelta(days=5)

        mock_contacts = [mock_contact1, mock_contact2]
        # Set up the mock session query chain
        mock_query = MockSession.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.all.return_value = mock_contacts
        # Call the method being tested
        result = CrudOps.get_upcoming_birthdays(MockSession, user=MagicMock())
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertIn(mock_contact1, result)
        self.assertIn(mock_contact2, result)

    @patch('src.contacts.models.Contact')
    @patch('src.contacts.crud.Session')
    def test_upcoming_birthdays_no_contacts(self, MockSession, MockContact):
        """Test case when there are no contacts with upcoming birthdays."""
        # Simulate no contacts returned from the database
        mock_contacts = []
        mock_query = MockSession.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.all.return_value = mock_contacts
        # Call the method being tested
        result = CrudOps.get_upcoming_birthdays(MockSession, user=MagicMock())
        # Assertions
        self.assertEqual(result, [])

    @patch('src.contacts.models.Contact')
    @patch('src.contacts.crud.Session')
    def test_upcoming_birthdays_adjust_to_weekend(self, MockSession, MockContact):
        """Test case for adjusting birthdays to the nearest weekend."""
        # Simulate today's date
        today = date.today()
        # Create mock contact with a weekday birthday
        mock_contact = MagicMock()
        mock_contact.first_name = "John"
        mock_contact.last_name = "Smith"
        # Set the birthday to a weekday (e.g., Wednesday)
        mock_contact.birthday = (today + timedelta(days=(3 - today.weekday()))).replace(year=2000)
        # Set up the mock session query chain
        mock_query = MockSession.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.all.return_value = [mock_contact]
        # Call the method being tested
        result = CrudOps.get_upcoming_birthdays(MockSession, user=MagicMock())
        # Verify that birthday is adjusted to the nearest weekend (Saturday or Sunday)
        adjusted_birthday = result[0].birthday
        self.assertTrue(adjusted_birthday.weekday() >= 5)  # Check if it's a weekend

    @patch('src.contacts.models.Contact')
    @patch('src.contacts.crud.Session')
    def test_upcoming_birthdays_no_birthday(self, MockSession, MockContact):
        """Test case for contacts without a birthday."""
        # Create mock contact with no birthday set
        mock_contact = MockContact(first_name="John", last_name="Smith", birthday=None)
        # Set up the mock session query chain
        mock_query = MockSession.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.all.return_value = [mock_contact]
        # Call the method being tested
        result = CrudOps.get_upcoming_birthdays(MockSession, user=MagicMock())
        # Assertions
        self.assertEqual(result, [])  # Should return an empty list as there's no birthday to compare


if __name__ == '__main__':
    unittest.main()
