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


def get_lemonade_request():
    request = {
        "image": "replicate:pollinations/lemonade-preset",
        "input": {
            "image": "https://store.pollinations.ai/ipfs/QmejbsQbhi4UsNGEeDSRszpzXv6W6CR61Gk2TZ53vQx5sT?filename=00003.png"
        },
    }
    return request


def get_wedatanation_request():
    request = {
        "description": "a nice bear with sunglasses",
        "user_id": "niels",
        "num_suggestions": 2,
    }
    return request


def get_stablediffusion_request():
    request = {
        "image": "614871946825.dkr.ecr.us-east-1.amazonaws.com/pollinations/stable-diffusion-private",
        "input": {
            "prompts": "A knight on a horse made out of stars and a galactic nebula"
        },
    }
    return request


def get_dreamachine_request():
    request = {
        "image": "replicate:pollinations/stable-diffusion-dreamachine",
        "input": {
            "prompts": "A rocket\nA pizza",
            "num_frames_per_prompt": 5,
        },
    }
    return request


if __name__ == "__main__":
    print(generate_pollinations_frontend_token())
