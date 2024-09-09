from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer
)
from sqlalchemy.orm import Session

from src.database import get_db
from src.auth.schemas import (
    UserScema,
    UserResponse,
    TokenModel
)
from src.auth.crud import (
    get_user_by_email,
    create_user,
    update_token
)
from src.auth.auth import auth_service as auth_s

auth_router = APIRouter(prefix='/api/auth', tags=["auth"])
get_refr_token = HTTPBearer()

@auth_router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    body: UserScema,
    db: Session = Depends(get_db)
):
    user_ = await get_user_by_email(body.email, db)
    if user_:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists"
        )
    body.password = auth_s.get_password_hash(body.password)
    new_user = await create_user(body, db)
    return {"user": new_user, "detail": "User successfully created"}


@auth_router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> TokenModel:
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
):
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
