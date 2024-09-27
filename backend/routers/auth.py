from datetime import timedelta

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.database import get_session
from ..core.security import create_access_token, decode_access_token
from ..crud.user import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_username,
)
from ..models.user import User
from ..schemas.token import Token
from ..schemas.user import UserCreate, UserOut

# OAuth2 scheme for extracting the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Create a router for authentication
router = APIRouter()


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)
) -> User:
    """
    Retrieve the current user based on the JWT token.
    """
    payload = decode_access_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the user is active.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/register", response_model=UserOut)
async def register_user(
    user_in: UserCreate = Body(...),
    db: AsyncSession = Depends(get_session),
):
    """
    Endpoint to register a new user.
    """
    # Check if the user already exists
    existing_user = await get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_user = await get_user_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = await create_user(db, user_in)

    return UserOut(
        id=str(new_user.id), email=new_user.email, username=new_user.username
    )


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=UserOut)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
):
    """
    Endpoint to retrieve the current authenticated user's information.
    """
    return UserOut(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
    )
