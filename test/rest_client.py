import requests
from utils import generate_test_token  # noqa F401
from utils import get_dreamachine_request  # noqa F401
from utils import get_lemonade_request  # noqa F401
from utils import get_replicate_stablediffusion_request  # noqa F401
from utils import get_stablediffusion_request  # noqa F401
from utils import get_wedatanation_request  # noqa F401

backend_url = "https://rest.pollinations.ai"
backend_url = "http://localhost:5000"
# backend_url = "https://worker-dev.pollinations.ai"


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


def client(request):
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
    client(get_replicate_stablediffusion_request())
