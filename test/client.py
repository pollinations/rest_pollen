import requests
from utils import generate_test_token


def get_stablediffusion_request():
    request = {
        "image": "614871946825.dkr.ecr.us-east-1.amazonaws.com/pollinations/stable-diffusion-private",
        "input": {
            "prompts": "A knight on a horse made out of stars and a galactic nebula"
        },
    }
    return request


def get_wedatanation_request():
    request = {
        "index_zip": "https://pollinations-ci-bucket.s3.amazonaws.com/clip-index.zip",
        "description": "An astronaut sloth",
        "user_id": "123",
        "num_suggestions": 5,
    }
    return request


def wedatanation_client():
    request = get_wedatanation_request()
    response = requests.post(
        "http://localhost:5000/wedatanation/avatar",
        json=request,
        headers={"Authorization": f"Bearer {generate_test_token()}"},
    )
    print(response.json())


if __name__ == "__main__":
    wedatanation_client()
