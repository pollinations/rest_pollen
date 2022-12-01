import click
import requests
from utils import generate_test_token  # noqa F401
from utils import get_dreamachine_request  # noqa F401
from utils import get_lemonade_request  # noqa F401
from utils import get_replicate_stablediffusion_request  # noqa F401
from utils import get_stablediffusion_request  # noqa F401
from utils import get_wedatanation_request  # noqa F401
from ws_client import WebsockerClosed, ws_client

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
    response.raise_for_status()


backends = {
    "prod": "https://rest.pollinations.ai",
    "dev": "https://worker-dev.pollinations.ai",
    "local": "http://localhost:5000",
}
backend_url = None


@click.command()
@click.argument("backend")
def main(backend):
    global backend_url
    backend_url = backends[backend]
    try:
        ws_client(backend, get_lemonade_request())
    except WebsockerClosed:
        pass
    # cached, lemonade
    client(get_lemonade_request())
    # cached, replicate backend
    client(get_dreamachine_request())
    # cached, pollinations backend
    client(get_stablediffusion_request())
    # uncached, replicate backend
    client(get_replicate_stablediffusion_request(True))
    # uncached, pollinations backend
    client(get_stablediffusion_request(True))


if __name__ == "__main__":
    main()
