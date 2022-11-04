from test.utils import generate_test_token

from fastapi.testclient import TestClient

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


if __name__ == "__main__":
    test_authentication()
