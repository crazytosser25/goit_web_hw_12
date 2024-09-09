"""Router for contast book"""
from typing import List
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from src.database import get_db

from src.contacts.schemas import ContactCreation, ContactScema
from src.contacts.crud import CrudOps

from src.auth.schemas import UserDb
from src.auth.auth import auth_service as auth_s


contact_router = APIRouter(prefix='/api/contacts', tags=["contacts"])


@contact_router.post("/", response_model=ContactScema)
def create_contact(
    contact: ContactCreation,
    db: Session = Depends(get_db),
    user: UserDb = Depends(auth_s.get_current_user)
) -> ContactScema:
    """Creates a new contact in the database.

    This endpoint allows the user to create a new contact by providing the
    necessary information such as first name, last name, email, phone number,
    birthday, and any additional data. The contact information is validated
    and then saved to the database.

    Args:
        contact (schemas.ContactCreation): The contact data required to create
            a new contact. This includes fields like first name, last name,
            email, phone number, and birthday.
        db (Session, optional): The database session used to interact with
            the database. It is provided by the dependency injection system
            through Depends(get_db).
        user (UserDb, optional): The currently authenticated user making the
            request. This dependency is resolved using
            Depends(auth_s.get_current_user) to ensure that the contact is
            associated with the correct user.

    Returns:
        schemas.Contact: The newly created contact with all the details
            including the assigned ID.
    """
    result =  CrudOps.create_contact(
        base=db,
        contact=contact,
        user=user
    )
    return result


@contact_router.get("/", response_model=list[ContactScema])
def read_contacts(
    db: Session = Depends(get_db),
    user: UserDb = Depends(auth_s.get_current_user)
) -> list[ContactScema]:
    """Retrieves a list of all contacts from the database.

    This endpoint fetches all contacts stored in the database and returns
    them as a list. It uses the provided database session to query the contacts
    table and retrieve all records.

    Args:
        db (Session, optional): The database session used to interact with
            the database.It is provided by dependency injection through
            Depends(get_db).
        user (UserDb, optional): The currently authenticated user making the
            request. This dependency is resolved using
            Depends(auth_s.get_current_user) to ensure that the contact is
            associated with the correct user.

    Returns:
        list[schemas.Contact]: A list of contacts, where each contact contains
            details such as first name, last name, email, phone number,
            birthday, and any additional information.
    """
    result = CrudOps.get_all_contacts(
        base=db,
        user=user
    )
    return result


@contact_router.get("/search/", response_model=List[ContactScema])
def search_contacts(
    query: str,
    db: Session = Depends(get_db),
    user: UserDb = Depends(auth_s.get_current_user)
) -> List[ContactScema]:
    """Searches for contacts based on a query string.

    This endpoint allows the user to search for contacts by matching the query
    string against the first name, last name, or email of the contacts in
    the database. It returns a list of contacts that match the search criteria.

    Args:
        query (str): The search term used to filter contacts. It can be part of
            the first name, last name, or email.
        db (Session, optional): The database session used to interact with
            the database, provided by dependency injection through
            Depends(get_db).
        user (UserDb, optional): The currently authenticated user making the
            request. This dependency is resolved using
            Depends(auth_s.get_current_user) to ensure that the contact is
            associated with the correct user.

    Returns:
        List[schemas.Contact]: A list of contacts that match the search
            criteria, including details such as first name, last name, email,
            phone number, birthday, and any additional information.
    """
    result = CrudOps.search_contacts(
        base=db,
        query=query,
        user=user
    )
    return result


@contact_router.get("/upcoming_birthdays/", response_model=List[ContactScema])
def upcoming_birthdays(
    db: Session = Depends(get_db),
    user: UserDb = Depends(auth_s.get_current_user)
) -> List[ContactScema]:
    """Retrieves contacts with upcoming birthdays within the next 7 days.

    This endpoint fetches contacts whose birthdays are occurring within the
    next 7 days from the current date. It uses the provided database session
    to query and return the matching contacts.

    Args:
        db (Session, optional): The database session used to interact with
            the database, provided by dependency injection through
            Depends(get_db).
        user (UserDb, optional): The currently authenticated user making the
            request. This dependency is resolved using
            Depends(auth_s.get_current_user) to ensure that the contact is
            associated with the correct user.

    Returns:
        List[schemas.Contact]: A list of contacts with upcoming birthdays,
            including details such as first name, last name, email,
            phone number, birthday, and any additional information.
    """
    result = CrudOps.get_upcoming_birthdays(
        base=db,
        user=user
    )
    return result


@contact_router.get("/{contact_id}", response_model=ContactScema)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    user: UserDb = Depends(auth_s.get_current_user)
) -> ContactScema:
    """Retrieves a specific contact by its ID from the database.

    This endpoint fetches the contact with the specified ID. If the contact
    is found, it returns the contact details; otherwise, it raises an
    HTTP 404 exception.

    Args:
        contact_id (int): The unique identifier of the contact to retrieve.
        db (Session, optional): The database session used to interact with t
            he database, provided by dependency injection through
            Depends(get_db).
        user (UserDb, optional): The currently authenticated user making the
            request. This dependency is resolved using
            Depends(auth_s.get_current_user) to ensure that the contact is
            associated with the correct user.

    Raises:
        HTTPException: If the contact with the given ID is not found, an
            HTTP 404 exception is raised with a message indicating that
            the contact was not found.

    Returns:
        schemas.Contact: The contact details of the specified contact ID,
            including fields such as first name, last name, email,
            phone number, birthday, and any additional information.
    """
    result = CrudOps.get_contact(
        base=db,
        id_=contact_id,
        user=user
    )
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )
    return result


@contact_router.put("/{contact_id}", response_model=ContactScema)
def update_contact(
    contact_id: int,
    contact: ContactCreation,
    db: Session = Depends(get_db),
    user: UserDb = Depends(auth_s.get_current_user)
) -> ContactScema:
    """Updates an existing contact in the database by its ID.

    This endpoint allows updating the details of an existing contact. It
    accepts the contact ID to identify which contact to update and the new
    contact data. If the contact with the specified ID is not found, it raises
    a 404 HTTP exception.

    Args:
        contact_id (int): The unique identifier of the contact to be updated.
        contact (schemas.ContactCreation): The new data for the contact,
            including fields such as first name, last name, email, phone
            number, birthday, and additional information.
        db (Session, optional): The database session used to interact with
            the database, provided by dependency injection through
            Depends(get_db).
        user (UserDb, optional): The currently authenticated user making the
            request. This dependency is resolved using
            Depends(auth_s.get_current_user) to ensure that the contact is
            associated with the correct user.

    Raises:
        HTTPException: If the contact with the given ID is not found, an
            HTTP 404 exception is raised with a message indicating that the
            contact was not found.

    Returns:
        schemas.Contact: The updated contact details, including the modified
            fields and other existing information.
    """
    result = CrudOps.update_contact(
        base=db,
        id_=contact_id,
        contact=contact,
        user=user
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )
    return result


@contact_router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    user: UserDb = Depends(auth_s.get_current_user)
) -> dict:
    """Deletes a contact from the database by its ID.

    This endpoint deletes the contact specified by the given ID. If the contact
    is found, it is removed from the database. If the contact is not found,
    an HTTP 404 exception is raised.

    Args:
        contact_id (int): The unique identifier of the contact to be deleted.
        db (Session, optional): The database session used to interact with the
            database, provided by dependency injection through Depends(get_db).
        user (UserDb, optional): The currently authenticated user making the
            request. This dependency is resolved using
            Depends(auth_s.get_current_user) to ensure that the contact is
            associated with the correct user.

    Raises:
        HTTPException: If the contact with the given ID is not found, an
            HTTP 404 exception is raised with a message indicating that the
            contact was not found.

    Returns:
        dict: A dictionary containing a message indicating that the contact was
            successfully deleted.
    """
    contact = CrudOps.delete_contact(
        base=db,
        id_=contact_id,
        user=user
    )

    if contact is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )
    result = {"details": "Contact deleted"}
    return result
