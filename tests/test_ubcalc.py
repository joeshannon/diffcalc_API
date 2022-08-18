import ast

import numpy as np
import pytest
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.hkl.geometry import Position
from diffcalc.ub.calc import UBCalculation
from fastapi.testclient import TestClient

from diffcalc_API.errors.ub import ErrorCodes
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


def test_get_ub(client: TestClient):
    response = client.get("/ub/test")

    assert ast.literal_eval(response.content.decode())["payload"] == (
        "UBCALC\n\n"
        + "   name:         dummy"
        + "\n\nREFERNCE\n\n"
        + "   n_hkl:      1.00000   0.00000   0.00000 <- set\n"
        + "   n_phi:    None"
        + "\n\nSURFACE NORMAL\n\n"
        + "   n_hkl:      0.00000   0.00000   1.00000\n"
        + "   n_phi:      0.00000   0.00000   1.00000 <- set"
        + "\n\nCRYSTAL\n\n"
        + "   <<< none specified >>>"
        + "\n\nUB MATRIX\n\n"
        + "   <<< none calculated >>>"
        + "\n\nREFLECTIONS\n\n"
        + "   <<< none specified >>>"
        + "\n\nCRYSTAL ORIENTATIONS\n\n"
        + "   <<< none specified >>>"
    )
    assert response.status_code == 200


def test_add_reflection(client: TestClient):
    response = client.post(
        "/ub/test/reflection?tag=foo",
        json={
            "hkl": {"h": 0, "k": 0, "l": 1},
            "position": {"mu": 7, "delta": 0, "nu": 10, "eta": 0, "chi": 0, "phi": 0},
            "energy": 12,
        },
    )

    assert response.status_code == 200
    assert dummy_hkl.ubcalc.get_reflection("foo")

    dummy_hkl.ubcalc.del_reflection("foo")


def test_edit_reflection(client: TestClient):
    dummy_hkl.ubcalc.add_reflection([0, 0, 1], Position(7, 0, 10, 0, 0, 0), 12, "foo")
    response = client.put(
        "/ub/test/reflection?tag=foo",
        json={"energy": 13, "set_tag": "bar"},
    )
    reflection = dummy_hkl.ubcalc.get_reflection("bar")

    assert response.status_code == 200
    assert reflection.energy == 13

    response_idx = client.put(
        "/ub/test/reflection?idx=0",
        json={"hkl": {"h": 0, "k": 3, "l": 1}},
    )

    assert response_idx.status_code == 200
    reflection_idx = dummy_hkl.ubcalc.get_reflection(0)

    assert reflection_idx.h == 0
    assert reflection_idx.k == 3
    assert reflection_idx.tag == "bar"

    dummy_hkl.ubcalc.del_reflection(0)


def test_delete_reflection(client: TestClient):
    dummy_hkl.ubcalc.add_reflection([0, 0, 1], Position(7, 0, 10, 0, 0, 0), 12, "foo")
    response = client.delete("/ub/test/reflection?tag=foo")

    assert response.status_code == 200
    with pytest.raises(Exception):
        dummy_hkl.ubcalc.get_reflection("foo")


def test_edit_or_delete_reflection_fails_for_non_existing_reflection(
    client: TestClient,
):
    edit_response = client.put(
        "/ub/test/reflection?tag=foo",
        json={"energy": 13},
    )
    delete_response = client.delete("/ub/test/reflection?tag=foo")

    assert edit_response.status_code == ErrorCodes.REFERENCE_RETRIEVAL_ERROR
    assert delete_response.status_code == ErrorCodes.REFERENCE_RETRIEVAL_ERROR


def test_add_orientation(client: TestClient):
    response = client.post(
        "/ub/test/orientation?tag=bar",
        json={
            "hkl": {"h": 0, "k": 1, "l": 0},
            "xyz": {"x": 0, "y": 1, "z": 0},
        },
    )

    assert response.status_code == 200
    assert dummy_hkl.ubcalc.get_orientation("bar")

    dummy_hkl.ubcalc.del_orientation("bar")


def test_edit_orientation(client: TestClient):
    dummy_hkl.ubcalc.add_orientation([0, 0, 1], [0, 0, 1], None, "bar")
    response = client.put(
        "/ub/test/orientation?tag=bar",
        json={"xyz": {"x": 1, "y": 1, "z": 0}, "set_tag": "bar"},
    )
    orientation = dummy_hkl.ubcalc.get_orientation("bar")

    assert response.status_code == 200

    assert orientation.x == 1
    assert orientation.y == 1
    assert orientation.z == 0

    dummy_hkl.ubcalc.del_orientation("bar")


def test_delete_orientation(client: TestClient):
    dummy_hkl.ubcalc.add_orientation([0, 0, 1], [0, 0, 1], None, "bar")
    response = client.delete("/ub/test/orientation?idx=0")

    assert response.status_code == 200
    with pytest.raises(Exception):
        dummy_hkl.ubcalc.get_orientation("bar")


def test_edit_or_delete_orientation_fails_for_non_existing_orientation(
    client: TestClient,
):
    edit_response = client.put(
        "/ub/test/orientation?tag=bar",
        json={"xyz": {"x": 1, "y": 1, "z": 0}},
    )
    delete_response = client.delete(
        "/ub/test/orientation?tag=bar",
    )

    assert edit_response.status_code == ErrorCodes.REFERENCE_RETRIEVAL_ERROR
    assert delete_response.status_code == ErrorCodes.REFERENCE_RETRIEVAL_ERROR


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
        response_with_wrong_input.status_code == ErrorCodes.INVALID_SET_LATTICE_PARAMS
    )
    assert response_with_no_input.status_code == ErrorCodes.INVALID_SET_LATTICE_PARAMS


def test_modify_property(client: TestClient):
    response = client.put(
        "/ub/test/n_hkl",
        json={"h": 0, "k": 0, "l": 1},
    )

    assert response.status_code == 200
    assert np.all(dummy_hkl.ubcalc.n_hkl == np.transpose([[0, 0, 1]]))


def test_modify_non_existent_property(client: TestClient):
    response = client.put(
        "/ub/test/silly_property",
        json={"h": 0, "k": 0, "l": 1},
    )
    assert response.status_code == ErrorCodes.INVALID_PROPERTY
