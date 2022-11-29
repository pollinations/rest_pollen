import requests
from utils import generate_test_token

backend_url = "https://rest.pollinations.ai"
backend_url = "http://localhost:5000"
# backend_url = "https://worker-dev.pollinations.ai"


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
        "description": "a nice bear with sunglasses",
        "user_id": "niels",
        "num_suggestions": 2,
    }
    return request


def wedatanation_client():
    request = get_wedatanation_request()
    response = requests.post(
        f"{backend_url}/wedatanation/avatar",
        json=request,
        headers={"Authorization": f"Bearer {generate_test_token()}"},
    )
    print(response.text)
    print(response)
    avatar = response.json()
    print(avatar)
    response = requests.post(
        f"{backend_url}/wedatanation/avatar/reserve",
        json=avatar,
        headers={"Authorization": f"Bearer {generate_test_token()}"},
    )
    print(response.json())


def get_lemonade_request():
    request = {
        "image": "replicate:pollinations/lemonade-preset",
        "input": {
            "image": "https://store.pollinations.ai/ipfs/QmejbsQbhi4UsNGEeDSRszpzXv6W6CR61Gk2TZ53vQx5sT?filename=00003.png"
        },
    }
    return request


def lemonade_client():
    request = get_lemonade_request()
    response = requests.post(
        f"{backend_url}/pollen",
        json=request,
        headers={"Authorization": f"Bearer {generate_test_token()}"},
    )
    print(response.text)
    print(response)


def get_dreamachine_request():
    request = {
        "image": "replicate:pollinations/stable-diffusion-dreamachine",
        # "image": "replicate:stability-ai/stable-diffusion",
        "input": {
            "prompts": "A pizza eating a banana\nA pizze with a fat belly",
            "num_frames_per_prompt": 20,
        },
    }
    return request


def dreamachine_client():
    request = get_dreamachine_request()
    response = requests.post(
        f"{backend_url}/pollen",
        json=request,
        headers={"Authorization": f"Bearer {generate_test_token()}"},
    )
    print(response.text)
    print(response)


if __name__ == "__main__":
    # wedatanation_client()
    # lemonade_client()
    dreamachine_client()
