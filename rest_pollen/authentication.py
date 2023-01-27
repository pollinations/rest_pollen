import datetime as dt
import os
from typing import Tuple

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from supabase import create_client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
supabase_api_key: str = os.environ.get("SUPABASE_API_KEY")
if url is not None:
    supabase = create_client(url, supabase_api_key)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

reuseable_oauth = OAuth2PasswordBearer(tokenUrl="/login", scheme_name="JWT")


class TokenPayload(BaseModel):
    sub: str
    exp: int
    token: str


class APIKeyNotFound(Exception):
    pass


async def get_current_user(token: str = Depends(reuseable_oauth)) -> dict:
    try:
        token_data, _ = get_token_payload(token)

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
    except APIKeyNotFound:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key not found, maybe it was revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


# @cache
def get_token_payload(token: str):
    try:
        payload = jwt.decode(
            token, JWT_SECRET, algorithms=[ALGORITHM], audience="authenticated"
        )
        if payload["aud"] == "api":
            raise JWTError
        client = create_client(url, supabase_api_key)
        db_client = client.postgrest
        db_client.auth(token)
    except JWTError:
        payload = resolve_api_token(token)
        db_client = supabase
    token_data = TokenPayload(**payload, token=token)
    return token_data, db_client


def resolve_api_token(token: str) -> Tuple[str, str]:
    """Check if the token is a valid API token and return the user id and the token"""
    payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM], audience="api")
    user_id = payload["sub"]
    if not check_api_token(user_id, token):
        raise APIKeyNotFound
    return payload


def check_api_token(user_id: str, token: str) -> bool:
    """Check if the token is valid for the user"""
    token = (
        supabase.table("api_tokens")
        .select("*")
        .eq("user", user_id)
        .eq("token", token)
        .execute()
        .data
    )
    return len(token) > 0


def create_api_token(user_id: str) -> str:
    """Create a new API token for the user.
    This is a token that needs to be checked in the db as users can revoke it."""
    payload = {
        "sub": f"{user_id}",
        "exp": dt.datetime.now() + dt.timedelta(days=180),
        "aud": "api",
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
    supabase.table("api_tokens").insert({"user": user_id, "token": token}).execute()
    return token


def get_api_tokens(user_id: str) -> list:
    """Get all API tokens for the user"""
    tokens = supabase.table("api_tokens").select("*").eq("user", user_id).execute().data
    return tokens


def revoke_api_token(user_id: str, token: str) -> bool:
    """Revoke an API token"""
    supabase.table("api_tokens").delete().eq("user", user_id).eq(
        "token", token
    ).execute()
