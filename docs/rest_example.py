import os

import requests

backend_url = "https://rest.pollinations.ai"

request = {
    "image": "pollinations/stable-diffusion-private",
    "input": {"prompts": "a horse made out of clouds"},
}

output = requests.post(
    f"{backend_url}/pollen",
    json=request,
    headers={"Authorization": f"Bearer {os.environ['POLLINATIONS_API_KEY']}"},
)

print(output.text)
