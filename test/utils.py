import datetime as dt
import random

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


def get_lemonade_request(uncached=False):
    request = {
        "image": "replicate:pollinations/lemonade-preset",
        "input": {
            "image": "https://store.pollinations.ai/ipfs/QmejbsQbhi4UsNGEeDSRszpzXv6W6CR61Gk2TZ53vQx5sT?filename=00003.png"
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
        "image": "replicate:pollinations/stable-diffusion-dreamachine",
        "input": {
            "prompts": "a statue of a woman\nA pizza with a fat belly",
            "num_frames_per_prompt": 4,
        },
    }
    if uncached:
        request["input"]["random"] = random.random()
    return request


if __name__ == "__main__":
    print(generate_pollinations_frontend_token())
