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


class TokenPayload(BaseModel):
    sub: str
    exp: int


async def get_current_user(token: str = Depends(reuseable_oauth)) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)

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
