import click
import requests
from utils import generate_test_token  # noqa F401
from utils import get_dreamachine_request  # noqa F401
from utils import get_dreamachine_request_pollinations  # noqa F401
from utils import get_lemonade_request  # noqa F401
from utils import get_replicate_stablediffusion_request  # noqa F401
from utils import get_stablediffusion_request  # noqa F401
from utils import get_wedatanation_request  # noqa F401
from ws_client import WebsockerClosed, ws_client  # noqa F401


def token_flow():
    """Test token flow.
    1. Create a new token
    2. get my tokens
    3. Use the token to make a request that writes something to the database
    4. delete token
    5. get my tokens, make sure the token is gone
    6. try to use the token to make a request that writes something to the database
    """
    token = generate_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{backend_url}/token/", headers=headers)
    original_tokens = response.json()
    print(original_tokens)
    response = requests.post(
        f"{backend_url}/token",
        headers=headers,
    )
    api_token = response.json()["token"]
    print(api_token)
    headers_api = {"Authorization": f"Bearer {api_token}"}
    response = requests.get(f"{backend_url}/token/", headers=headers_api)
    print(response.json())
    # assert the new token is in the list
    assert api_token in [i["token"] for i in response.json()]
    # Do something with the token
    request = get_stablediffusion_request(True)
    response = requests.post(
        f"{backend_url}/pollen/", json=request, headers=headers_api
    )
    print(response.json())
    assert response.status_code == 200
    # Delete the token
    response = requests.delete(f"{backend_url}/token/{api_token}", headers=headers)
    print(response.json())
    # Make sure the token is gone
    response = requests.get(f"{backend_url}/token/", headers=headers)
    print(response.json())
    assert api_token not in [i["token"] for i in response.json()]
    # Try to do something with the token
    request = get_stablediffusion_request(True)
    response = requests.post(
        f"{backend_url}/pollen/", json=request, headers=headers_api
    )
    print(response.json())
    assert response.status_code == 401
    print("Token flow test passed!")


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


def get_mine():
    token = generate_test_token()
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwNTU1MzhjNy02NzM1LTQyZTUtYjYyMy05MTczZTEzYjA2YTkiLCJleHAiOjE2ODg5MzYzNTAsImF1ZCI6ImFwaSJ9.R_vcDIk-xlYmJdGX9Yz6Sg8xAl3Ym0zI6FrByJvndqg"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{backend_url}/mine/", headers=headers)
    assert response.status_code == 200


def client(request):
    print("<<<<<<<<<", request["image"])
    response = requests.post(
        f"{backend_url}/pollen",
        json=request,
        headers={"Authorization": f"Bearer {generate_test_token()}"},
    )
    print(response)
    try:
        print(response.json())
    except Exception:
        print(response.text)
    response.raise_for_status()
    print(request["image"], ">>>>>>>>>")
    input()


backends = {
    "prod": "https://rest.pollinations.ai",
    "dev": "https://worker-dev.pollinations.ai",
    "local": "http://localhost:6000",
}
backend_url = None


@click.command()
@click.argument("backend")
def main(backend):
    global backend_url
    backend_url = backends[backend]
    token_flow()
    # get_mine()
    # # # lemonade
    # client(get_lemonade_request(True))
    # # # dreamachine
    # client(get_dreamachine_request_pollinations())
    # client(get_dreamachine_request_pollinations(True))
    # client(get_dreamachine_request())
    # client(get_dreamachine_request(True))

    # # stable diffusion
    # client(get_replicate_stablediffusion_request(True))
    # client(get_stablediffusion_request(True))
    # try:
    #     ws_client(backend, get_lemonade_request())
    # except WebsockerClosed:
    #     pass


if __name__ == "__main__":
    main()
