import requests
from utils import generate_test_token

request = {"image": "test-image", "input": {"test": "test"}}


response = requests.post(
    "http://localhost:5000/pollen",
    json=request,
    headers={"Authorization": f"Bearer {generate_test_token()}"},
)

print(response, response.text)
