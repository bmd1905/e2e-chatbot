from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.config import settings
from ..core.database import get_session
from ..models.user import User
from ..schemas.token import Token, TokenData
from ..schemas.user import UserCreate, UserOut

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for extracting the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Create a router for authentication
router = APIRouter()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hashed version.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password for storage.
    """
    return pwd_context.hash(password)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Retrieve a user from the database by username.
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Retrieve a user from the database by email.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[User]:
    """
    Authenticate a user by username/email and password.
    """
    user = await get_user_by_username(db, username)
    if not user:
        user = await get_user_by_email(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)
) -> User:
    """
    Retrieve the current user based on the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except (InvalidTokenError, AttributeError):
        raise credentials_exception
    user = await get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
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

    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        username=user_in.username,
        password_hash=hashed_password,
        is_active=True,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserOut(
        id=str(new_user.id), email=new_user.email, username=new_user.username
    )


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """
    Authenticate the user and return an access token.

    - **Parameters**:
      - **form_data**: The OAuth2 form data containing username and password.
      - **db**: Database session dependency.
    - **Returns**: A JWT access token.
    """

    # Authenticate the user
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Raise an HTTP 401 Unauthorized error if authentication fails
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, email, or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a new access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Return the access token
    return Token(access_token=access_token, token_type="bearer")


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
