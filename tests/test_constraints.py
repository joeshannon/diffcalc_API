import ast

import pytest
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation
from fastapi.testclient import TestClient

from diffcalc_API.errors.constraints import Codes
from diffcalc_API.server import app
from diffcalc_API.stores.protocol import HklCalcStore, get_store
from tests.conftest import FakeHklCalcStore

dummy_hkl = HklCalculation(UBCalculation(name="dummy"), Constraints())


def dummy_get_store() -> HklCalcStore:
    return FakeHklCalcStore(dummy_hkl)


@pytest.fixture(scope="session")
def client() -> TestClient:
    app.dependency_overrides[get_store] = dummy_get_store

    return TestClient(app)


def test_set_constraints(client: TestClient):
    response = client.post(
        "/constraints/test?collection=B07",
        json={
            "delta": 1,
            "bin_eq_bout": 1,
            "mu": 2,
        },
    )

    assert response.status_code == 200
    assert dummy_hkl.constraints.asdict == {
        "delta": 1.0,
        "bin_eq_bout": True,
        "mu": 2.0,
    }


def test_set_varying_number_of_constraints_and_with_incorrect_fields(
    client: TestClient,
):
    wrong_field_response = client.post(
        "/constraints/test",
        json={
            "fakeField": 10,
        },
    )

    assert wrong_field_response.status_code == 400
    assert (
        ast.literal_eval(wrong_field_response._content.decode())["type"]
        == "<class 'diffcalc.util.DiffcalcException'>"
    )

    too_many_fields_response = client.post(
        "/constraints/test",
        json={"delta": 1, "bin_eq_bout": 1, "mu": 2, "omega": 5},
    )

    assert too_many_fields_response.status_code == 200
    assert dummy_hkl.constraints.asdict == {
        "delta": 1.0,
        "bin_eq_bout": True,
        "omega": 5.0,
    }

    dummy_hkl.constraints = Constraints()
    too_few_fields_response = client.post(
        "/constraints/test",
        json={"delta": 1, "bin_eq_bout": 1},
    )

    assert too_few_fields_response.status_code == 200


def test_set_and_remove_constraint(client: TestClient):
    dummy_hkl.constraints = Constraints()
    set_response = client.patch(
        "/constraints/test/alpha",
        json=1,
    )

    assert set_response.status_code == 200
    assert dummy_hkl.constraints.asdict == {"alpha": 1.0}

    remove_response = client.delete("/constraints/test/alpha")

    assert remove_response.status_code == 200
    assert dummy_hkl.constraints.asdict == {}


def test_set_or_remove_nonexisting_constraint(client: TestClient):
    dummy_hkl.constraints = Constraints()
    set_response = client.patch(
        "/constraints/test/fake",
        json=1,
    )

    assert set_response.status_code == Codes.CHECK_CONSTRAINT_EXISTS
    assert dummy_hkl.constraints.asdict == {}

    remove_response = client.delete("/constraints/test/fake")

    assert remove_response.status_code == Codes.CHECK_CONSTRAINT_EXISTS
    assert dummy_hkl.constraints.asdict == {}
