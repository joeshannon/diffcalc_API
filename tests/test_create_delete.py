import pytest
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation
from fastapi.testclient import TestClient

from diffcalc_api.server import app
from diffcalc_api.stores.protocol import HklCalcStore, get_store
from tests.conftest import FakeHklCalcStore

dummy_hkl = HklCalculation(UBCalculation(name="dummy"), Constraints())


def dummy_get_store() -> HklCalcStore:
    return FakeHklCalcStore(dummy_hkl)


@pytest.fixture(scope="session")
def client() -> TestClient:
    app.dependency_overrides[get_store] = dummy_get_store

    return TestClient(app)


def test_create(client: TestClient):
    response = client.post(
        "/test?collection=B07",
    )

    assert response.status_code == 200


def test_delete(client: TestClient):
    response = client.delete(
        "/test?collection=B07",
    )

    assert response.status_code == 200
