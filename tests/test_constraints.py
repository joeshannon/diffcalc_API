import ast

import pytest
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation
from fastapi.testclient import TestClient

from diffcalc_API.errors.Constraints import codes
from diffcalc_API.persistence import HklCalcStore, get_store
from diffcalc_API.server import app
from tests.conftest import FakeHklCalcStore

dummyHkl = HklCalculation(UBCalculation(name="dummy"), Constraints())


def dummy_get_store() -> HklCalcStore:
    return FakeHklCalcStore(dummyHkl)


@pytest.fixture(scope="session")
def client() -> TestClient:
    app.dependency_overrides[get_store] = dummy_get_store

    return TestClient(app)


def test_set_constraints(client: TestClient):
    response = client.put(
        "/constraints/test/set",
        json={
            "delta": 1,
            "bin_eq_bout": 1,
            "mu": 2,
        },
    )

    assert response.status_code == 200
    assert dummyHkl.constraints.asdict == {"delta": 1.0, "bin_eq_bout": True, "mu": 2.0}


def test_set_varying_number_of_constraints_and_with_incorrect_fields(
    client: TestClient,
):
    wrongFieldResponse = client.put(
        "/constraints/test/set",
        json={
            "fakeField": 10,
        },
    )

    assert wrongFieldResponse.status_code == 400  # make this more concrete.
    assert (
        ast.literal_eval(wrongFieldResponse._content.decode())["type"]
        == "<class 'diffcalc.util.DiffcalcException'>"
    )

    tooManyFieldsResponse = client.put(
        "/constraints/test/set",
        json={"delta": 1, "bin_eq_bout": 1, "mu": 2, "omega": 5},
    )

    assert tooManyFieldsResponse.status_code == 200
    assert dummyHkl.constraints.asdict == {
        "delta": 1.0,
        "bin_eq_bout": True,
        "omega": 5.0,
    }

    dummyHkl.constraints = Constraints()
    tooFewFieldsResponse = client.put(
        "/constraints/test/set",
        json={"delta": 1, "bin_eq_bout": 1},
    )

    assert tooFewFieldsResponse.status_code == 200


def test_set_and_remove_constraint(client: TestClient):
    dummyHkl.constraints = Constraints()
    setResponse = client.patch(
        "/constraints/test/constrain/alpha",
        json=1,
    )

    assert setResponse.status_code == 200
    assert dummyHkl.constraints.asdict == {"alpha": 1.0}

    removeResponse = client.patch("/constraints/test/unconstrain/alpha")

    assert removeResponse.status_code == 200
    assert dummyHkl.constraints.asdict == {}


def test_set_or_remove_nonexisting_constraint(client: TestClient):
    dummyHkl.constraints = Constraints()
    setResponse = client.patch(
        "/constraints/test/constrain/fake",
        json=1,
    )

    assert setResponse.status_code == codes.check_constraint_exists
    assert dummyHkl.constraints.asdict == {}

    removeResponse = client.patch("/constraints/test/unconstrain/fake")

    assert removeResponse.status_code == codes.check_constraint_exists
    assert dummyHkl.constraints.asdict == {}
