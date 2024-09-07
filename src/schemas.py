"""Schemas for check"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class ContactBasic(BaseModel):
    """A Pydantic model for basic contact information.

    This model defines the schema for the contact's essential details, including
    names, email, phone number, birthday, and additional information. It is used
    for validation and serialization/deserialization of contact data.

    Args:
        BaseModel (BaseModel): The base class for Pydantic models, providing validation
            and serialization capabilities.

    Attributes:
        first_name (str): The first name of the contact. Maximum length is 50 characters.
        last_name (str): The last name of the contact. Maximum length is 50 characters.
        email (EmailStr): The contact's email address, validated as a proper email format.
        phone_number (str): The contact's phone number. Maximum length is 12 characters.
        birthday (date): The contact's birthday in `YYYY-MM-DD` format.
        other_info (Optional[str]): Additional information about the contact. Maximum
            length is 250 characters. This field is optional.
    """
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone_number: str = Field(max_length=12)
    birthday: date
    other_info: Optional[str] = Field(max_length=250)

class ContactCreation(ContactBasic):
    """A Pydantic model for creating a new contact.

    This model extends `ContactBasic` and is used when creating a new contact. It includes
    all the fields from `ContactBasic` but does not add any additional fields or validation
    rules.

    Args:
        ContactBasic (BaseModel): Inherits validation and serialization capabilities from
            `ContactBasic`.
    """


class Contact(ContactBasic):
    """A Pydantic model for contact data including an ID.

    This model extends `ContactBasic` by adding an `id` field. It is used to represent a
    contact record retrieved from the database, which includes all basic contact details
    along with a unique identifier.

    Args:
        ContactBasic (BaseModel): Inherits fields and validation from `ContactBasic`.

    Attributes:
        id (int): The unique identifier of the contact.
    """
    id: int
