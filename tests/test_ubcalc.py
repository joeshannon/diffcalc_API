import pytest
from fastapi.testclient import TestClient

# from diffcalc_API.routes.UBCalculation import router
from diffcalc_API.server import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_read_main(client: TestClient):
    response = client.get("/ub/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
