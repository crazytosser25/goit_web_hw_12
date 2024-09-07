"""Main file"""
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import engine, get_db

import src.contacts.models as models
import src.contacts.schemas as schemas
import contacts.crud as crud


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/api/healthchecker")
def root() -> dict:
    """Health check endpoint to verify that the server is running.

    This endpoint can be used to confirm that the server is alive and
    responding to requests. It returns a simple message indicating the server
    status.

    Returns:
        dict: A dictionary containing a message indicating that
            the server is alive.
    """
    result = {"message": "Server alive."}
    return result

@app.post("/contacts/", response_model=schemas.Contact)
def create_contact(
    contact: schemas.ContactCreation,
    db: Session = Depends(get_db)
) -> schemas.Contact:
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

    Returns:
        schemas.Contact: The newly created contact with all the details
            including the assigned ID.
    """
    result =  crud.create_contact(base=db, contact=contact)
    return result

@app.get("/contacts/", response_model=list[schemas.Contact])
def read_contacts(
    db: Session = Depends(get_db)
) -> list[schemas.Contact]:
    """Retrieves a list of all contacts from the database.

    This endpoint fetches all contacts stored in the database and returns
    them as a list. It uses the provided database session to query the contacts
    table and retrieve all records.

    Args:
        db (Session, optional): The database session used to interact with
            the database.It is provided by dependency injection through
            Depends(get_db).

    Returns:
        list[schemas.Contact]: A list of contacts, where each contact contains
            details such as first name, last name, email, phone number,
            birthday, and any additional information.
    """
    result = crud.get_all_contacts(base=db)
    return result

@app.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db)
) -> schemas.Contact:
    """Retrieves a specific contact by its ID from the database.

    This endpoint fetches the contact with the specified ID. If the contact
    is found, it returns the contact details; otherwise, it raises an
    HTTP 404 exception.

    Args:
        contact_id (int): The unique identifier of the contact to retrieve.
        db (Session, optional): The database session used to interact with t
            he database, provided by dependency injection through
            Depends(get_db).

    Raises:
        HTTPException: If the contact with the given ID is not found, an
            HTTP 404 exception is raised with a message indicating that
            the contact was not found.

    Returns:
        schemas.Contact: The contact details of the specified contact ID,
            including fields such as first name, last name, email,
            phone number, birthday, and any additional information.
    """
    result = crud.get_contact(base=db, id_=contact_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )
    return result

@app.get("/contacts/search/", response_model=List[schemas.Contact])
def search_contacts(
    query: str,
    db: Session = Depends(get_db)
) -> List[schemas.Contact]:
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

    Returns:
        List[schemas.Contact]: A list of contacts that match the search
            criteria, including details such as first name, last name, email,
            phone number, birthday, and any additional information.
    """
    result = crud.search_contacts(
        base=db,
        query=query
    )
    return result

@app.get("/contacts/upcoming_birthdays/", response_model=List[schemas.Contact])
def upcoming_birthdays(
    db: Session = Depends(get_db)
) -> List[schemas.Contact]:
    """Retrieves contacts with upcoming birthdays within the next 7 days.

    This endpoint fetches contacts whose birthdays are occurring within the
    next 7 days from the current date. It uses the provided database session
    to query and return the matching contacts.

    Args:
        db (Session, optional): The database session used to interact with
            the database, provided by dependency injection through
            Depends(get_db).

    Returns:
        List[schemas.Contact]: A list of contacts with upcoming birthdays,
            including details such as first name, last name, email,
            phone number, birthday, and any additional information.
    """
    result = crud.get_upcoming_birthdays(base=db)
    return result

@app.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(
    contact_id: int,
    contact: schemas.ContactCreation,
    db: Session = Depends(get_db)
) -> schemas.Contact:
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

    Raises:
        HTTPException: If the contact with the given ID is not found, an
            HTTP 404 exception is raised with a message indicating that the
            contact was not found.

    Returns:
        schemas.Contact: The updated contact details, including the modified
            fields and other existing information.
    """
    result = crud.update_contact(
        base=db,
        id_=contact_id,
        contact=contact
    )
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )
    return result

@app.delete("/contacts/{contact_id}")
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Deletes a contact from the database by its ID.

    This endpoint deletes the contact specified by the given ID. If the contact
    is found, it is removed from the database. If the contact is not found,
    an HTTP 404 exception is raised.

    Args:
        contact_id (int): The unique identifier of the contact to be deleted.
        db (Session, optional): The database session used to interact with the
            database, provided by dependency injection through Depends(get_db).

    Raises:
        HTTPException: If the contact with the given ID is not found, an
            HTTP 404 exception is raised with a message indicating that the
            contact was not found.

    Returns:
        dict: A dictionary containing a message indicating that the contact was
            successfully deleted.
    """
    contact = crud.delete_contact(
        base=db,
        id_=contact_id
    )
    if contact is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )
    result = {"details": "Contact deleted"}
    return result
