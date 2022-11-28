import datetime as dt

from fastapi.testclient import TestClient
from jose import jwt

from rest_pollen.authentication import ALGORITHM, JWT_SECRET
from rest_pollen.main import app

client = TestClient(app)


def generate_test_token() -> str:
    """For debugging only: generate a token for a given username"""
    to_encode = {
        "sub": "testuser",
        "exp": dt.datetime.utcnow() + dt.timedelta(minutes=30),
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def generate_wedatanation_token() -> str:
    """For debugging only: generate a token for a given username"""
    to_encode = {
        "sub": "wedatanation-dev",
        "exp": dt.datetime.utcnow() + dt.timedelta(days=180),
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def generate_pollinations_frontend_token() -> str:
    """For debugging only: generate a token for a given username"""
    to_encode = {
        "sub": "pollinations-generic-frontend",
        "exp": dt.datetime.utcnow() + dt.timedelta(days=180),
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


if __name__ == "__main__":
    print(generate_pollinations_frontend_token())
