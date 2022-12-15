from test.utils import get_wedatanation_request  # noqa F401
from test.utils import (
    generate_test_token,
    get_dreamachine_request,
    get_dreamachine_request_pollinations,
)

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from rest_pollen.main import app

client = TestClient(app)


def test_authentication() -> None:
    token = generate_test_token()
    response = client.get("/user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    response = client.get("/user")
    assert response.status_code == 401
    response = client.get("/user", headers={"Authorization": f"Bearer {token}1"})
    assert response.status_code == 403


# def test_wedatanation() -> None:
#     request = get_wedatanation_request()
#     response = client.post(
#         "/wedatanation/avatar",
#         json=request,
#         headers={"Authorization": f"Bearer {generate_test_token()}"},
#     )
#     assert response.status_code == 200
#     avatar = response.json()
#     assert len(avatar["images"]) == request["num_suggestions"]
#     # response = client.post(
#     #     "/wedatanation/avatar/reserve",
#     #     json=avatar,
#     #     headers={"Authorization": f"Bearer {generate_test_token()}"},
#     # )


def test_replicate_backend():
    request = get_dreamachine_request()
    response = client.post(
        "/pollen",
        json=request,
        headers={"Authorization": f"Bearer {generate_test_token()}"},
    )
    assert response.status_code == 200


def test_pollinations_backend():
    request = get_dreamachine_request_pollinations(True)
    response = client.post(
        "/pollen",
        json=request,
        headers={"Authorization": f"Bearer {generate_test_token()}"},
    )
    assert response.status_code == 200


def test_websocket():
    client = TestClient(app)
    token = generate_test_token()
    with client.websocket_connect(f"/ws?token={token}") as ws:
        ws.send_json(get_dreamachine_request())
        data = ws.receive_json()
        assert data["input"] == get_dreamachine_request()["input"]


def test_websocket_authentication_no_token():
    client = TestClient(app)
    connection_accepted = False
    try:
        with client.websocket_connect("/ws"):
            connection_accepted = True
    except AttributeError:
        pass
    assert not connection_accepted


def test_websocket_authentication_invalid_token():
    client = TestClient(app)
    connection_accepted = False
    try:
        with client.websocket_connect("/ws?token=nonsense"):
            connection_accepted = True
    except WebSocketDisconnect:
        pass
    assert not connection_accepted


def test_post_retrieve_dict() -> None:
    token = generate_test_token()
    data = {"image": "image", "input": {"a": 1}}
    response = client.post(
        "/store", json=data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    cid = response.json()
    response = client.get(f"/store/{cid}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == data
    response = client.get(
        f"/store/{cid}/input", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == data["input"]


def test_post_retrieve_list() -> None:
    token = generate_test_token()
    data = [0, 1, 2, 3]
    response = client.post(
        "/store", json=data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    cid = response.json()
    response = client.get(f"/store/{cid}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == data
    response = client.get(
        f"/store/{cid}/0", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == data[0]
