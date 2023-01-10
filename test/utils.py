import datetime as dt
import random

from fastapi.testclient import TestClient
from jose import jwt

from rest_pollen.authentication import ALGORITHM, JWT_SECRET
from rest_pollen.db_client import create_client, supabase_api_key, url
from rest_pollen.main import app

client = TestClient(app)


# def generate_test_token() -> str:
#     """For debugging only: generate a token for a given username"""
#     to_encode = {
#         "sub": "testuser",
#         "exp": dt.datetime.utcnow() + dt.timedelta(minutes=30),
#     }
#     encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
#     return encoded_jwt


def generate_test_token() -> str:
    client = create_client(url, supabase_api_key)
    random_password: str = "fqj13bnf2hiu23h"
    email = "niels@pollinations.ai"
    session = client.auth.sign_in(email=email, password=random_password)
    return session.access_token


def generate_token(username) -> str:
    to_encode = {
        "sub": username,
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


def get_lemonade_request(uncached=False):
    request = {
        "image": "replicate:pollinations/lemonade-preset",
        "input": {
            "image": "https://www.ifolor.de/content/dam/ifolor/inspire-gallery/inspirationen/selbstportraet-selfie/inspire_selbstportraet_selfie_1200px_header.jpg.transform/w1440/q90/image.jpg?inspire_selbstportraet_selfie_1200px_header.jpg"
        },
    }
    if uncached:
        request["input"]["random"] = random.random()
    return request


def get_wedatanation_request(uncached=False):
    request = {
        "description": "a nice bear with sunglasses",
        "user_id": "niels",
        "num_suggestions": 2,
    }
    if uncached:
        request["input"]["random"] = random.random()
    return request


def get_stablediffusion_request(uncached=False):
    request = {
        "image": "614871946825.dkr.ecr.us-east-1.amazonaws.com/pollinations/stable-diffusion-private",
        "input": {"prompts": "horse"},
    }
    if uncached:
        request["input"]["random"] = random.random()
    return request


def get_replicate_stablediffusion_request(uncached=False):
    request = {
        "image": "replicate:stability-ai/stable-diffusion",
        "input": {"prompt": "horse"},
    }
    if uncached:
        request["input"]["random"] = random.random()
    return request


def get_dreamachine_request(uncached=False):
    request = {
        "image": "replicate:pollinations/animate",
        "input": {
            "prompt_start": "sideview of a small monkey, white background",
            "prompt_end": "sideview of a human walking, white background",
        },
    }
    if uncached:
        request["input"]["random"] = random.random()
    return request


def get_dreamachine_request_pollinations(uncached=False):
    request = {
        "image": "pollinations/animate",
        "input": {
            "prompt_start": "sideview of a small monkey, white background, by Vincent van Gogh",
            "prompt_end": "sideview of a human walking, white background, by Vincent van Gogh",
        },
    }
    if uncached:
        request["input"]["random"] = random.random()
    return request


if __name__ == "__main__":
    # print(generate_pollinations_frontend_token())
    print(generate_token(username="niels"))
