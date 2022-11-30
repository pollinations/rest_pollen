import requests
from utils import (
    generate_test_token,
    get_dreamachine_request,
    get_lemonade_request,
    get_wedatanation_request,
)

backend_url = "https://rest.pollinations.ai"
backend_url = "https://worker-dev.pollinations.ai"
backend_url = "http://localhost:5000"


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


def lemonade_client():
    request = get_lemonade_request()
    response = requests.post(
        f"{backend_url}/pollen",
        json=request,
        headers={"Authorization": f"Bearer {generate_test_token()}"},
    )
    print(response.text)
    print(response)


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
    lemonade_client()
    # dreamachine_client()
