import datetime as dt
import os
import random

from fastapi.testclient import TestClient
from jose import jwt
from supabase import create_client

from rest_pollen.authentication import ALGORITHM, JWT_SECRET
from rest_pollen.db_client import supabase_api_key, url
from rest_pollen.main import app

client = TestClient(app)


def invite_user(email, password) -> str:
    client = create_client(url, supabase_api_key)
    try:
        session = client.auth.sign_in(email=email, password=password)
    except:  # noqa
        client.auth.sign_up(email=email, password=password)
        session = client.auth.sign_in(email=email, password=password)
    return session.access_token


# def generate_test_token() -> str:
#     client = create_client(url, supabase_api_key)
#     random_password: str = os.environ.get("TEST_USER_PASSWORD", "test")
#     email = "niels@pollinations.ai"
#     session = client.auth.sign_in(email=email, password=random_password)
#     return session.access_token


def generate_test_token() -> str:
    return os.environ.get("POLLINATIONS_API_TOKEN")


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
        "description": "a hippie Sloth with sunglasses",
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
