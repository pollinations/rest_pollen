import requests
from utils import generate_test_token

request = {
    "image": "614871946825.dkr.ecr.us-east-1.amazonaws.com/pollinations/stable-diffusion-private",
    "input": {"prompts": "A knight on a horse made out of stars and a galactic nebula"},
}


response = requests.post(
    "http://localhost:5000/pollen",
    json=request,
    headers={"Authorization": f"Bearer {generate_test_token()}"},
)

print(response, response.text)
breakpoint()
