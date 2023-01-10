import datetime as dt
import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError

load_dotenv()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

reuseable_oauth = OAuth2PasswordBearer(tokenUrl="/login", scheme_name="JWT")


def log_and_run(func):
    def wrapper(*args, **kwargs):
        print(f"Running {func.__name__}", args, kwargs)
        return func(*args, **kwargs)

    return wrapper


# reuseable_oauth = log_and_run(reuseable_oauth)


class TokenPayload(BaseModel):
    sub: str
    exp: int
    token: str


async def get_current_user(token: str = Depends(reuseable_oauth)) -> dict:
    try:
        token_data = get_token_payload(token)

        if dt.datetime.fromtimestamp(token_data.exp) < dt.datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


def get_token_payload(token: str) -> dict:
    payload = jwt.decode(
        token, JWT_SECRET, algorithms=[ALGORITHM], audience="authenticated"
    )
    token_data = TokenPayload(**payload, token=token)
    return token_data
