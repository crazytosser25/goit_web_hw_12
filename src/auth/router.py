"""Router for authentification"""
from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database import get_db

from src.auth.schemas import UserScema, UserResponse, TokenModel, RequestEmail
from src.auth.crud import get_user_by_email, create_user, update_token, confirmed_check_toggle
from src.auth.auth import auth_service as auth_s
from src.auth.mail import send_email


auth_router = APIRouter(prefix='/api/auth', tags=["auth"])
get_refr_token = HTTPBearer()


@auth_router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    body: UserScema,
    bt: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    """Handles user registration by creating a new user account.

    This endpoint allows a new user to register by providing their username, email, and password.
    The password is hashed before being stored in the database. If the email is already in use,
    an HTTP 409 Conflict error is raised.

    Args:
        body (UserScema): The request body containing the new user's data, including
            username, email, and password.
        db (Session, optional): The database session dependency, automatically injected by FastAPI.

    Raises:
        HTTPException: If the email provided is already associated with an existing account,
        a 409 Conflict error is raised with the message "Account already exists".

    Returns:
        dict: A dictionary containing the newly created user's data and a success message.
            The dictionary includes:
            - "user": The `UserDb` model instance representing the new user.
            - "detail": A message indicating the user was successfully created.
    """
    user_ = await get_user_by_email(body.email, db)

    if user_:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists"
        )

    body.password = auth_s.get_password_hash(body.password)
    new_user = await create_user(body, db)

    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return {
        "user": new_user,
        "detail": "User successfully created. Check your email for confirmation."
    }


@auth_router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> TokenModel:
    """Authenticates a user and generates access and refresh tokens.

    This endpoint allows a registered user to log in by providing their email (as username)
    and password. If the credentials are correct, it returns a pair of JWT tokens:
    an access token and a refresh token. If the credentials are incorrect, an appropriate
    HTTP error is raised.

    Args:
        body (OAuth2PasswordRequestForm, optional): The login form data containing the username
        (email) and password. This is automatically populated by FastAPI using dependency injection.
        db (Session, optional): The database session dependency, automatically injected by FastAPI.

    Raises:
        HTTPException: If the user does not exist, a 404 Not Found error is raised
            with the message "Invalid data".
        HTTPException: If the password is incorrect, a 401 Unauthorized error is raised
            with the message "Invalid data".

    Returns:
        TokenModel: An object containing the access token, refresh token,
            and the token type (bearer).
    """
    user = await get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid data"
        )

    if not auth_s.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid data"
        )

    if user.confirmed is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not confirmed"
        )

    access_token_ = await auth_s.create_access_token(data={"sub": user.email})
    refresh_token_ = await auth_s.create_refresh_token(data={"sub": user.email})

    await update_token(user, refresh_token_, db)
    return {
        "access_token": access_token_,
        "refresh_token": refresh_token_,
        "token_type": "bearer"
    }


@auth_router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(get_refr_token),
    db: Session = Depends(get_db)
) -> TokenModel:
    """Refreshes the JWT access and refresh tokens for a user.

    This endpoint allows a user to obtain a new pair of access and refresh tokens using
    a valid refresh token. It validates the provided refresh token, ensures it matches the one
    stored in the database, and then generates new tokens. If the refresh token is invalid or
    does not match, an error is raised.

    Args:
        credentials (HTTPAuthorizationCredentials, optional): The credentials object containing
            the refresh token. This is automatically provided via dependency injection using
            the `Security` dependency with `get_refr_token`.
        db (Session, optional): The database session dependency, automatically injected by FastAPI.

    Raises:
        HTTPException: If the refresh token is invalid or does not match the one stored in
            the user's record, a 401 Unauthorized error is raised with
            the message "Invalid refresh token".

    Returns:
        TokenModel: An object containing the new access token, refresh token, a
            nd the token type (bearer).
    """
    token = credentials.credentials
    email = await auth_s.decode_refresh_token(token)
    user = await get_user_by_email(email, db)

    if user.refresh_token != token:
        await update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    access_token = await auth_s.create_access_token(data={"sub": email})
    refresh_token_ = await auth_s.create_refresh_token(data={"sub": email})

    await update_token(user, refresh_token_, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_,
        "token_type": "bearer"
    }


@auth_router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)) -> dict:
    email = await auth_s.get_email_from_token(token)
    user = await get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await confirmed_check_toggle(email, db)
    return {"message": "Email confirmed"}


@auth_router.post('/request_email')
async def request_email(
    body: RequestEmail,
    bt: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    user = await get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        bt.add_task(send_email, user.email, user.username, request.base_url)

    return {"message": "Check your email for confirmation."}
