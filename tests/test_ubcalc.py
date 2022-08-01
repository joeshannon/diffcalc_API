import numpy as np
import pytest
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.hkl.geometry import Position
from diffcalc.ub.calc import UBCalculation
from fastapi.testclient import TestClient

from diffcalc_API.errors.ub import Codes
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


def test_add_reflection(client: TestClient):
    response = client.post(
        "/ub/test/reflection",
        json={
            "hkl": [0, 0, 1],
            "position": [7, 0, 10, 0, 0, 0],
            "energy": 12,
            "tag": "foo",
        },
    )

    assert response.status_code == 200
    assert dummy_hkl.ubcalc.get_reflection("foo")

    dummy_hkl.ubcalc.del_reflection("foo")


def test_edit_reflection(client: TestClient):
    dummy_hkl.ubcalc.add_reflection([0, 0, 1], Position(7, 0, 10, 0, 0, 0), 12, "foo")
    response = client.put(
        "/ub/test/reflection",
        json={
            "energy": 13,
            "tag_or_idx": "foo",
        },
    )
    reflection = dummy_hkl.ubcalc.get_reflection("foo")

    assert response.status_code == 200
    assert reflection.energy == 13

    dummy_hkl.ubcalc.del_reflection("foo")


def test_delete_reflection(client: TestClient):
    dummy_hkl.ubcalc.add_reflection([0, 0, 1], Position(7, 0, 10, 0, 0, 0), 12, "foo")
    response = client.delete("/ub/test/reflection", json={"tag_or_idx": "foo"})

    assert response.status_code == 200
    with pytest.raises(Exception):
        dummy_hkl.ubcalc.get_reflection("foo")


def test_edit_or_delete_reflection_fails_for_non_existing_reflection(
    client: TestClient,
):
    edit_response = client.put(
        "/ub/test/reflection",
        json={
            "energy": 13,
            "tag_or_idx": "foo",
        },
    )
    delete_response = client.delete(
        "/ub/test/reflection",
        json={"tag_or_idx": "foo"},
    )

    assert edit_response.status_code == Codes.REFERENCE_RETRIEVAL_ERROR
    assert delete_response.status_code == Codes.REFERENCE_RETRIEVAL_ERROR


def test_add_orientation(client: TestClient):
    response = client.post(
        "/ub/test/orientation",
        json={
            "hkl": [0, 1, 0],
            "xyz": [0, 1, 0],
            "tag": "bar",
        },
    )

    assert response.status_code == 200
    assert dummy_hkl.ubcalc.get_orientation("bar")

    dummy_hkl.ubcalc.del_orientation("bar")


def test_edit_orientation(client: TestClient):
    dummy_hkl.ubcalc.add_orientation([0, 0, 1], [0, 0, 1], None, "bar")
    response = client.put(
        "/ub/test/orientation",
        json={
            "xyz": [1, 1, 0],
            "tag_or_idx": "bar",
        },
    )
    orientation = dummy_hkl.ubcalc.get_orientation("bar")

    assert response.status_code == 200

    assert orientation.x == 1
    assert orientation.y == 1
    assert orientation.z == 0

    dummy_hkl.ubcalc.del_orientation("bar")


def test_delete_orientation(client: TestClient):
    dummy_hkl.ubcalc.add_orientation([0, 0, 1], [0, 0, 1], None, "bar")
    response = client.delete(
        "/ub/test/orientation",
        json={"tag_or_idx": "bar"},
    )

    assert response.status_code == 200
    with pytest.raises(Exception):
        dummy_hkl.ubcalc.get_orientation("bar")


def test_edit_or_delete_orientation_fails_for_non_existing_orientation(
    client: TestClient,
):
    edit_response = client.put(
        "/ub/test/orientation",
        json={
            "xyz": [1, 1, 0],
            "tag_or_idx": "bar",
        },
    )
    delete_response = client.delete(
        "/ub/test/orientation",
        json={"tag_or_idx": "bar"},
    )

    assert edit_response.status_code == Codes.REFERENCE_RETRIEVAL_ERROR
    assert delete_response.status_code == Codes.REFERENCE_RETRIEVAL_ERROR


def test_set_lattice(client: TestClient):
    response = client.patch(
        "/ub/test/lattice",
        json={"a": 2},
    )

    assert response.status_code == 200
    assert dummy_hkl.ubcalc.crystal


def test_set_lattice_fails_for_empty_data(client: TestClient):
    response_with_no_input = client.patch(
        "/ub/test/lattice",
        json={},
    )

    response_with_wrong_input = client.patch(
        "/ub/test/lattice",
        json={"unknown": "fields"},
    )

    assert (
        response_with_wrong_input.status_code == Codes.INVALID_SET_LATTICE_PARAMS_ERROR
    )
    assert response_with_no_input.status_code == Codes.INVALID_SET_LATTICE_PARAMS_ERROR


def test_modify_property(client: TestClient):
    response = client.put(
        "/ub/test/n_hkl",
        json=[0, 0, 1],
    )

    assert response.status_code == 200
    assert np.all(dummy_hkl.ubcalc.n_hkl == np.transpose([[0, 0, 1]]))


def test_modify_non_existent_property(client: TestClient):
    response = client.put(
        "/ub/test/silly_property",
        json=[0, 0, 1],
    )
    assert response.status_code == Codes.INVALID_PROPERTY_ERROR
