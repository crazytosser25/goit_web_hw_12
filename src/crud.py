"""CRUD operations"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
import src.models as models
import src.schemas as schemas


def create_contact(
    base: Session,
    contact: schemas.ContactCreation
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

    Returns:
        models.Contact: The newly created contact record from the database,
            containing all its details including the automatically generated
            fields like ID.
    """
    base_contact = models.Contact(**contact.model_dump())
    base.add(base_contact)
    base.commit()
    base.refresh(base_contact)
    return base_contact

def get_contact(
    base: Session,
    id_: int
) -> models.Contact:
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
    result = base.query(models.Contact).filter(models.Contact.id == id_).first()
    return result

def get_all_contacts(
    base: Session
) -> List[models.Contact]:
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
    return base.query(models.Contact).all()

def search_contacts(
    base: Session,
    query: str
) -> List[models.Contact]:
    """Searches for contacts that match the given query string.

    This function searches for contacts where the query string matches any
    part of the contact's first name, last name, or email. The search is
    case-insensitive and uses partial matching to find relevant contacts.

    Args:
        base (Session): The database session used to interact with the database.
        query (str): The search term used to filter contacts. It will be
            matched against the contact's first name, last name, and email fields.

    Returns:
        list[models.Contact]: A list of contact objects that match the search
            criteria. Each contact object includes details such as first name,
            last name, email, phone number, birthday, and any
            additional information.
    """
    result = base.query(models.Contact).filter(
        or_(
            models.Contact.first_name.ilike(f"%{query}%"),
            models.Contact.last_name.ilike(f"%{query}%"),
            models.Contact.email.ilike(f"%{query}%")
        )
    ).all()
    return result

def get_upcoming_birthdays(
    base: Session
) -> List[models.Contact]:
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

    Returns:
        List[models.Contact]: A list of contact objects with birthdays occurring in the
        next 7 days. Each contact includes details such as first name, last name, email,
        phone number, birthday, and any additional information. If no contacts have
        upcoming birthdays, an empty list is returned.
    """
    days = 7
    today = datetime.now().date()

    result = []
    contacts = base.query(models.Contact).all()
    for contact in contacts:
        birth_date = contact.birthday
        try:
            birthday_this_year = birth_date.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birth_date.replace(year=today.year+1)
        except TypeError:
            continue

        if 0 <= (birthday_this_year - today).days <= days:
            if birthday_this_year.weekday() >= 5:
                days_ahead = 0 - birthday_this_year.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                birthday_this_year += timedelta(days=days_ahead)
            contact.birthday = birthday_this_year
            result.append(contact)
    if result:
        return result
    return []

def update_contact(
    base: Session,
    id_: int,
    contact: schemas.ContactCreation
) -> models.Contact:
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

    Returns:
        models.Contact: The updated contact object if the contact was found and updated.
            If the contact with the given ID does not exist, it returns `None`.
    """
    result = base.query(models.Contact).filter(models.Contact.id == id_).first()
    if result:
        for key, value in contact.model_dump().items():
            setattr(result, key, value)
        base.commit()
        base.refresh(result)
    return result

def delete_contact(
    base: Session,
    id_: int
) -> models.Contact:
    """Deletes a contact from the database by its ID.

    This function locates a contact using the provided ID and removes it from the
    database. If the contact is found, it is deleted and the changes are committed
    to the database. The function returns the deleted contact if it was found and
    removed. If no contact with the given ID is found, the function returns `None`.

    Args:
        base (Session): The database session used to interact with the database.
        id_ (int): The unique identifier of the contact to be deleted.

    Returns:
        models.Contact: The deleted contact object if it was found and removed.
        If no contact with the given ID exists, it returns `None`.
    """
    result = base.query(models.Contact).filter(models.Contact.id == id_).first()
    if result:
        base.delete(result)
        base.commit()
    return result
