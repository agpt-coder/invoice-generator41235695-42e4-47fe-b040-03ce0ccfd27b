from datetime import datetime

import prisma
import prisma.models
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel


class LoginUserOutput(BaseModel):
    """
    This model represents the response returned after successful user authentication, primarily consisting of the access token.
    """

    access_token: str
    token_type: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "YOUR_SECRET_KEY"

ALGORITHM = "HS256"


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the password provided by the user matches the hashed password stored in the database.

    Args:
    plain_password (str): The plain text password provided by the user.
    hashed_password (str): The hashed password stored in the database for a user.

    Returns:
    bool: True if the password matches the stored hashed password, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


async def get_user_by_email(email: str) -> prisma.models.User | None:
    """
    Retrieve a user from the database by their email address.

    Args:
    email (str): The email address of the user.

    Returns:
    User | None: The user object if found, None otherwise.
    """
    return await prisma.models.User.prisma().find_unique(where={"email": email})


async def authenticate_user(email: str, password: str) -> prisma.models.User | None:
    """
    Authenticate a user based on email and password.

    Args:
    email (str): The email of the user trying to authenticate.
    password (str): The password of the user trying to authenticate.

    Returns:
    User | None: The authenticated user object if authentication succeeds, None otherwise.
    """
    user = await get_user_by_email(email)
    if user and await verify_password(password, user.password):
        return user
    return None


async def create_access_token(data: dict, expires_delta=None) -> str:
    """
    Creates a JWT access token using the provided data and expiry details.

    Args:
    data (dict): The payload data to encode within the JWT token.
    expires_delta (Optional[datetime.timedelta]): The expiry span of the token. None for no expiry.

    Returns:
    str: The JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def login_user(email: str, password: str) -> LoginUserOutput:
    """
    Authenticates user and returns a token.

    Args:
    email (str): The email address of the user trying to log in.
    password (str): The password for the user trying to log in.

    Returns:
    LoginUserOutput: This model represents the response returned after successful user authentication, primarily consisting of the access token.
    """
    user = await authenticate_user(email, password)
    if not user:
        raise ValueError("Invalid authentication credentials.")
    access_token = await create_access_token(data={"sub": user.email})
    return LoginUserOutput(access_token=access_token, token_type="Bearer")
