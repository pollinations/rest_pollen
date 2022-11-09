from test.utils import generate_test_token

from fastapi.testclient import TestClient

from rest_pollen.main import app

client = TestClient(app)


def get_wedatanation_request():
    request = {
        "description": "An astronaut sloth",
        "user_id": "987",
        "num_suggestions": 2,
    }
    return request


def test_authentication() -> None:
    token = generate_test_token()
    response = client.get("/user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    response = client.get("/user")
    assert response.status_code == 401
    response = client.get("/user", headers={"Authorization": f"Bearer {token}1"})
    assert response.status_code == 403


def test_wedatanation() -> None:
    request = get_wedatanation_request()
    response = client.post(
        "/wedatanation/avatar",
        json=request,
        headers={"Authorization": f"Bearer {generate_test_token()}"},
    )
    assert response.status_code == 200
    avatar = response.json()
    assert len(avatar["images"]) == request["num_suggestions"]
    # response = client.post(
    #     "/wedatanation/avatar/reserve",
    #     json=avatar,
    #     headers={"Authorization": f"Bearer {generate_test_token()}"},
    # )


if __name__ == "__main__":
    test_authentication()
