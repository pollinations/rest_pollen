from test.utils import (  # noqa F401
    generate_test_token,
    get_dreamachine_request,
    get_dreamachine_request_pollinations,
    get_stablediffusion_request,
    get_wedatanation_request,
)

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from rest_pollen.main import app
from rest_pollen.s3_wrapper import legacy_store

client = TestClient(app)


def test_authentication() -> None:
    token = generate_test_token()
    response = client.get("/user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    response = client.get("/user")
    assert response.status_code == 401
    response = client.get("/user", headers={"Authorization": f"Bearer {token}1"})
    assert response.status_code == 403


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
    response = client.get("/token/", headers=headers)
    original_tokens = response.json()
    print(original_tokens)
    response = client.post(
        "/token",
        headers=headers,
    )
    api_token = response.json()["token"]
    print(api_token)
    headers_api = {"Authorization": f"Bearer {api_token}"}
    response = client.get("/token/", headers=headers_api)
    print(response.json())
    # assert the new token is in the list
    assert api_token in [i["token"] for i in response.json()]
    # Do something with the token
    request = get_stablediffusion_request(True)
    response = client.post("/pollen/", json=request, headers=headers_api)
    print(response.json())
    assert response.status_code == 200
    # Delete the token
    response = client.delete(f"/token/{api_token}", headers=headers)
    print(response.json())
    # Make sure the token is gone
    response = client.get("/token/", headers=headers)
    print(response.json())
    assert api_token not in [i["token"] for i in response.json()]
    # Try to do something with the token
    request = get_stablediffusion_request(True)
    response = client.post("/pollen/", json=request, headers=headers_api)
    print(response.json())
    assert response.status_code == 401
    print("Token flow test passed!")


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


def test_store():
    # test if legacy ipfs works the same as official ipfs store
    token = generate_test_token()
    input_cid = "QmPPT9pDcXWrCU8H7DF9gzUFRH8LPkV2nLjfNUbdRLN11H"
    data_rest_store = client.get(f"/store/{input_cid}").json()
    assert "input" in data_rest_store
    data_ipfs_store = legacy_store(input_cid)
    assert data_rest_store == data_ipfs_store
    # test if it works the same for the /pollen endpoint
    data_rest_pollen = client.get(
        f"/pollen/{input_cid}", headers={"Authorization": f"Bearer {token}"}
    ).json()
    assert "output" in data_rest_pollen
    # data_ipfs_pollen = legacy_store(input_cid, "pollen")
    # assert data_rest_pollen == data_ipfs_pollen

    # test the new ids
    input_cid = "s3:b20a66e5f378993d110bcda860376844b1c971d500ddb6e636263a8f7250b535"
    data_rest_store = client.get(f"/store/{input_cid}").json()
    assert "input" in data_rest_store
    data_rest_pollen = client.get(
        f"/pollen/{input_cid}", headers={"Authorization": f"Bearer {token}"}
    ).json()
    assert "output" in data_rest_pollen
    print(data_rest_pollen)


if __name__ == "__main__":
    test_store()


def test_replicate_backend():
    request = get_dreamachine_request()
    response = client.post(
        "/pollen",
        json=request,
        headers={"Authorization": f"Bearer {generate_test_token()}"},
    )
    assert response.status_code == 200


def test_pollinations_backend():
    request = get_stablediffusion_request(True)
    print(request)
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


def test_different_users() -> None:
    token1 = generate_test_token()
    token2 = generate_test_token()
    data = get_dreamachine_request_pollinations()
    response1 = client.post(
        "/pollen", json=data, headers={"Authorization": f"Bearer {token1}"}
    )
    assert response1.status_code == 200
    response2 = client.post(
        "/pollen", json=data, headers={"Authorization": f"Bearer {token2}"}
    )
    assert response2.status_code == 200
    assert response1.json()["cid"] == response2.json()["cid"]
