"""CRUD operations"""
import calendar
from datetime import datetime, timedelta
from typing import List, Type, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

import src.contacts.models as models
import src.contacts.schemas as schemas

from src.auth.schemas import UserDb


class CrudOps:
    """Class to import all CRUD operation in one peace."""
    @staticmethod
    def create_contact(
        base: Session,
        contact: schemas.ContactCreation,
        user: UserDb
    ) -> models.Contact:
        """Creates a new contact in the database.

        This function accepts a contact creation schema, converts it into a
        database model, and adds the new contact to the database. It then commits
        the transaction to save the new contact and refreshes the session to
        retrieve the full data of the newly created contact.

        Args:
            base (Session): The database session used to interact with the database.
            contact (schemas.ContactCreation): The data required to create a new
                contact, including fields such as first name, last name, email,
                phone number, birthday, and any additional information.
            user (UserDb): The currently authenticated user who is creating the contact.
                This user will be associated with the contact.

        Returns:
            models.Contact: The newly created contact record from the database,
                containing all its details including the automatically generated
                fields like ID.
        """
        new_contact = models.Contact(**contact.model_dump(), user_id=user.id)
        base.add(new_contact)
        base.commit()
        base.refresh(new_contact)
        return new_contact

    @staticmethod
    def get_contact(
        base: Session,
        id_: int,
        user: UserDb
    ) -> Type[models.Contact] | None:
        """Retrieves a contact from the database by its ID.

        This function queries the database to find and return the contact with the
        specified ID. If the contact exists, it returns the contact object;
        otherwise, it returns `None`.

        Args:
            base (Session): The database session used to interact with the database.
            id_ (int): The unique identifier of the contact to retrieve.

        Returns:
            models.Contact: The contact object corresponding to the specified ID.
                If no contact with the given ID is found, it returns `None`.
        """
        result = base.query(models.Contact).filter(
            models.Contact.user_id == user.id,
            models.Contact.id == id_
        ).first()
        return result

    @staticmethod
    def get_all_contacts(
        base: Session,
        user: UserDb
    ) -> list[Type[models.Contact]]:
        """Retrieves all contacts from the database.

        This function queries the database to retrieve and return a list of all
        contact records. It fetches every contact stored in the database and
        returns them as a list.

        Args:
            base (Session): The database session used to interact with the database.

        Returns:
            list[models.Contact]: A list of contact objects representing all
                contacts in the database. Each contact includes details such as
                first name, last name, email, phone number, birthday, and any
                additional information.
        """
        return base.query(models.Contact).filter(
            models.Contact.user_id == user.id
        ).all()

    @staticmethod
    def search_contacts(
        base: Session,
        query: str,
        user: UserDb
    ) -> list[Type[models.Contact]]:
        """Searches for contacts that match the given query string.

        This function searches for contacts where the query string matches any
        part of the contact's first name, last name, or email. The search is
        case-insensitive and uses partial matching to find relevant contacts.

        Args:
            base (Session): The database session used to interact with the database.
            query (str): The search term used to filter contacts. It will be
                matched against the contact's first name, last name, and email fields.
            user (UserDb): The currently authenticated user who is creating the contact.
                This user will be associated with the contact.

        Returns:
            list[models.Contact]: A list of contact objects that match the search
                criteria. Each contact object includes details such as first name,
                last name, email, phone number, birthday, and any
                additional information.
        """
        result = base.query(models.Contact).filter(
            models.Contact.user_id == user.id,
            or_(
                models.Contact.first_name.ilike(f"%{query}%"),
                models.Contact.last_name.ilike(f"%{query}%"),
                models.Contact.email.ilike(f"%{query}%")
            )
        ).all()
        return result

    @staticmethod
    def get_upcoming_birthdays(
        base: Session,
        user: UserDb
    ) -> list[Type[models.Contact]] | list[Any]:
        """Retrieves contacts with birthdays occurring in the next 7 days.

        This function searches through all contacts in the database to find those whose
        birthdays fall within the next 7 days from the current date. It calculates the
        upcoming birthdays by comparing the contact's birth date with the current date
        and determines if the birthday is within the specified range. Contacts with
        upcoming birthdays are adjusted to the nearest weekend day (Saturday or Sunday)
        if they fall on a weekday.

        Args:
            base (Session): The database session used to query and interact with
                the database.
            user (UserDb): The currently authenticated user who is creating the contact.
                This user will be associated with the contact.

        Returns:
            List[models.Contact]: A list of contact objects with birthdays occurring in the
            next 7 days. Each contact includes details such as first name, last name, email,
            phone number, birthday, and any additional information. If no contacts have
            upcoming birthdays, an empty list is returned.
        """
        days = 7
        today = datetime.now().date()
        result = []

        contacts = base.query(models.Contact).filter(
            models.Contact.user_id == user.id
        ).all()

        for contact in contacts:
            birth_date = contact.birthday
            try:
                if birth_date.month == 2 and birth_date.day == 29:
                    if not calendar.isleap(today.year):
                        birthday_this_year = birth_date.replace(year=today.year, day=28)
                    else:
                        birthday_this_year = birth_date.replace(year=today.year)
                else:
                    birthday_this_year = birth_date.replace(year=today.year)

                if birthday_this_year < today:
                    if birth_date.month == 2 and birth_date.day == 29 and not calendar.isleap(today.year + 1):
                        birthday_this_year = birth_date.replace(year=today.year + 1, day=28)
                    else:
                        birthday_this_year = birth_date.replace(year=today.year + 1)

            except TypeError:
                continue

            if 0 <= (birthday_this_year - today).days <= days:
                if birthday_this_year.weekday() < 5:  # Weekday
                    days_until_weekend = 5 - birthday_this_year.weekday()
                    birthday_this_year += timedelta(days=days_until_weekend)

                contact.birthday = birthday_this_year
                result.append(contact)
        if result:
            return result
        return []

    @staticmethod
    def update_contact(
        base: Session,
        id_: int,
        contact: schemas.ContactCreation,
        user: UserDb
    ) -> Type[models.Contact] | None:
        """Updates an existing contact in the database with new data.

        This function locates a contact by its ID and updates its attributes with the data
        provided in the `contact` schema. If the contact is found, its fields are updated
        with the new values, the changes are committed to the database, and the updated
        contact is returned. If the contact with the given ID is not found, the function
        returns `None`.

        Args:
            base (Session): The database session used to interact with the database.
            id_ (int): The unique identifier of the contact to be updated.
            contact (schemas.ContactCreation): The new data for the contact, which includes
                fields such as first name, last name, email, phone number, birthday, and
                any additional information.
            user (UserDb): The currently authenticated user who is creating the contact.
                This user will be associated with the contact.

        Returns:
            models.Contact: The updated contact object if the contact was found and updated.
                If the contact with the given ID does not exist, it returns `None`.
        """
        result = base.query(models.Contact).filter(
            models.Contact.user_id == user.id,
            models.Contact.id == id_
        ).first()

        if result:
            for key, value in contact.model_dump().items():
                setattr(result, key, value)
            base.commit()
            base.refresh(result)
        return result

    @staticmethod
    def delete_contact(
        base: Session,
        id_: int,
        user: UserDb
    ) -> Type[models.Contact] | None:
        """Deletes a contact from the database by its ID.

        This function locates a contact using the provided ID and removes it from the
        database. If the contact is found, it is deleted and the changes are committed
        to the database. The function returns the deleted contact if it was found and
        removed. If no contact with the given ID is found, the function returns `None`.

        Args:
            base (Session): The database session used to interact with the database.
            id_ (int): The unique identifier of the contact to be deleted.
            user (UserDb): The currently authenticated user who is creating the contact.
                This user will be associated with the contact.

        Returns:
            models.Contact: The deleted contact object if it was found and removed.
            If no contact with the given ID exists, it returns `None`.
        """
        result = base.query(models.Contact).filter(
            models.Contact.user_id == user.id,
            models.Contact.id == id_
        ).first()
        if result:
            base.delete(result)
            base.commit()
        return result
