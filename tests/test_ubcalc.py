import ast
from ast import literal_eval

import numpy as np
import pytest
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.hkl.geometry import Position
from diffcalc.ub.calc import UBCalculation
from fastapi.testclient import TestClient

from diffcalc_api.errors.ub import ErrorCodes, NoUbMatrixError
from diffcalc_api.server import app
from diffcalc_api.stores.protocol import get_store
from tests.conftest import FakeHklCalcStore


class Client:
    def __init__(self, hkl):
        self.hkl = hkl

    @property
    def client(self):
        app.dependency_overrides[get_store] = lambda: FakeHklCalcStore(self.hkl)
        return TestClient(app)


@pytest.fixture
def client_generator(request) -> Client:
    """Create tester object"""
    return Client(request.param)


def test_get_ub():
    hkl = HklCalculation(UBCalculation("dummy"), Constraints())
    client = Client(hkl).client

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


def test_add_reflection():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    response = client.post(
        "/ub/test/reflection?tag=foo",
        json={
            "hkl": {"h": 0, "k": 0, "l": 1},
            "position": {
                "mu": 7,
                "delta": 0,
                "nu": 10,
                "eta": 0,
                "chi": 0,
                "phi": 0,
            },
            "energy": 12,
        },
    )

    assert response.status_code == 200
    assert ubcalc.get_reflection("foo")


def test_edit_reflection():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ubcalc.add_reflection([0, 0, 1], Position(7, 0, 10, 0, 0, 0), 12, "foo")
    response = client.put(
        "/ub/test/reflection?tag=foo",
        json={"energy": 13, "set_tag": "bar"},
    )
    reflection = ubcalc.get_reflection("bar")

    assert response.status_code == 200
    assert reflection.energy == 13

    response_idx = client.put(
        "/ub/test/reflection?idx=0",
        json={"hkl": {"h": 0, "k": 3, "l": 1}},
    )

    assert response_idx.status_code == 200
    reflection_idx = ubcalc.get_reflection(0)

    assert reflection_idx.h == 0
    assert reflection_idx.k == 3
    assert reflection_idx.tag == "bar"


def test_delete_reflection():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ubcalc.add_reflection([0, 0, 1], Position(7, 0, 10, 0, 0, 0), 12, "foo")
    response = client.delete("/ub/test/reflection?tag=foo")

    assert response.status_code == 200
    with pytest.raises(Exception):
        ubcalc.get_reflection("foo")


def test_edit_or_delete_reflection_fails_for_non_existing_reflection():
    hkl = HklCalculation(UBCalculation(), Constraints())
    client = Client(hkl).client

    edit_response = client.put(
        "/ub/test/reflection?tag=foo",
        json={"energy": 13},
    )
    delete_response = client.delete("/ub/test/reflection?tag=foo")

    assert edit_response.status_code == ErrorCodes.REFERENCE_RETRIEVAL_ERROR
    assert delete_response.status_code == ErrorCodes.REFERENCE_RETRIEVAL_ERROR


def test_add_orientation():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    response = client.post(
        "/ub/test/orientation?tag=bar",
        json={
            "hkl": {"h": 0, "k": 1, "l": 0},
            "xyz": {"x": 0, "y": 1, "z": 0},
        },
    )

    assert response.status_code == 200
    assert ubcalc.get_orientation("bar")


def test_edit_orientation():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ubcalc.add_orientation([0, 0, 1], [0, 0, 1], None, "bar")
    response = client.put(
        "/ub/test/orientation?tag=bar",
        json={"xyz": {"x": 1, "y": 1, "z": 0}, "set_tag": "bar"},
    )
    orientation = ubcalc.get_orientation("bar")

    assert response.status_code == 200

    assert orientation.x == 1
    assert orientation.y == 1
    assert orientation.z == 0


def test_delete_orientation():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ubcalc.add_orientation([0, 0, 1], [0, 0, 1], None, "bar")
    response = client.delete("/ub/test/orientation?idx=0")

    assert response.status_code == 200
    with pytest.raises(Exception):
        ubcalc.get_orientation("bar")


def test_edit_or_delete_orientation_fails_for_non_existing_orientation():
    hkl = HklCalculation(UBCalculation(), Constraints())
    client = Client(hkl).client

    edit_response = client.put(
        "/ub/test/orientation?tag=bar",
        json={"xyz": {"x": 1, "y": 1, "z": 0}},
    )
    delete_response = client.delete(
        "/ub/test/orientation?tag=bar",
    )

    assert edit_response.status_code == ErrorCodes.REFERENCE_RETRIEVAL_ERROR
    assert delete_response.status_code == ErrorCodes.REFERENCE_RETRIEVAL_ERROR


def test_set_lattice():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    response = client.patch(
        "/ub/test/lattice",
        json={"a": 2},
    )

    assert response.status_code == 200
    assert ubcalc.crystal


def test_set_lattice_fails_for_empty_data():
    hkl = HklCalculation(UBCalculation(), Constraints())
    client = Client(hkl).client
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


def test_get_miscut():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ubcalc.add_reflection(
        (0, 0, 1), Position(7.31, 0, 10.62, 0, 0, 0), 12.39842, "refl"
    )
    ubcalc.add_orientation((0, 1, 0), (0, 1, 0), tag="plane")

    ubcalc.set_lattice("", 4.913, 5.405)
    ubcalc.calc_ub("refl", "plane")
    response = client.get("/ub/test/miscut?collection=B07")

    response_dict = literal_eval(response.content.decode())["payload"]

    assert response_dict["rotation_axis"]["x"] == pytest.approx(-1.0)
    assert response_dict["rotation_axis"]["y"] == pytest.approx(0)
    assert response_dict["rotation_axis"]["z"] == pytest.approx(0)


def test_get_miscut_fails_when_no_ub_matrix():
    hkl = HklCalculation(UBCalculation(), Constraints())
    client = Client(hkl).client

    response = client.get("/ub/test/miscut?collection=B07")

    response_with_hkl = client.get(
        "/ub/test/miscut/hkl?collection=B07",
        params={
            "h": 1,
            "k": 0,
            "l": 1,
            "mu": 45,
            "delta": 90,
            "nu": 15,
            "eta": 20,
            "chi": 90,
            "phi": 35,
        },
    )

    assert response.status_code == ErrorCodes.NO_UB_MATRIX_ERROR
    assert response_with_hkl.status_code == ErrorCodes.NO_UB_MATRIX_ERROR
    assert (
        literal_eval(response.content.decode())["message"] == NoUbMatrixError().detail
    )
    assert (
        literal_eval(response_with_hkl.content.decode())["message"]
        == NoUbMatrixError().detail
    )


def test_get_miscut_from_hkl():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ubcalc.add_reflection(
        (0, 0, 1), Position(7.31, 0, 10.62, 0, 0, 0), 12.39842, "refl"
    )
    ubcalc.add_orientation((0, 1, 0), (0, 1, 0), tag="plane")
    ubcalc.set_lattice("", 4.913, 5.405)
    ubcalc.calc_ub("refl", "plane")

    response = client.get(
        "/ub/test/miscut/hkl?collection=B07",
        params={
            "h": 0,
            "k": 0,
            "l": 1,
            "mu": 90,
            "delta": 90,
            "nu": 90,
            "eta": 90,
            "chi": 90,
            "phi": 90,
        },
    )

    assert response.status_code == 200


def test_set_miscut():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client
    assert ubcalc.U is None

    response = client.put(
        "/ub/test/miscut?collection=B07",
        params={"angle": 0.035, "add_miscut": False},
        json={"x": -1, "y": 0, "z": 0},
    )

    assert response.status_code == 200
    assert ubcalc.U is not None


def test_calc_ub():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ubcalc.set_lattice("SiO2", 4.913, 5.405)
    ubcalc.n_hkl = (1, 0, 0)
    ubcalc.add_reflection(
        (0, 0, 1), Position(7.31, 0, 10.62, 0, 0, 0), 12.39842, "refl1"
    )
    ubcalc.add_orientation((0, 1, 0), (0, 1, 0), None, "plane")
    ubcalc.calc_ub("refl1", "plane")

    response = client.get(
        "/ub/test/ub", params={"first_tag": "refl1", "second_tag": "plane"}
    )
    expected_ub = [
        [
            1.27889,
            -0.0,
            0.0,
        ],
        [-0.0, 1.278111, 0.04057],
        [-0.0, -0.044633, 1.161768],
    ]

    assert response.status_code == 200
    assert ast.literal_eval(response.content.decode())["payload"] == expected_ub


def test_calc_ub_fails_when_incorrect_tags():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ubcalc.set_lattice("SiO2", 4.913, 5.405)
    response = client.get("/ub/test/ub", params={"tag1": "one", "idx2": 2})

    assert response.status_code == 400


def test_set_u():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    u_matrix = np.identity(3)
    client.put("/ub/test/u?collection=B07", json=u_matrix.tolist())

    assert np.all(ubcalc.U == u_matrix)


def test_set_ub():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ub_matrix = np.identity(3)
    client.put("/ub/test/ub?collection=B07", json=ub_matrix.tolist())

    assert np.all(ubcalc.U == ub_matrix)


def test_modify_property():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client
    response = client.put(
        "/ub/test/n_hkl",
        json={"h": 0, "k": 0, "l": 1},
    )

    assert response.status_code == 200
    assert np.all(ubcalc.n_hkl == np.transpose([[0, 0, 1]]))


def test_modify_non_existent_property():
    hkl = HklCalculation(UBCalculation(), Constraints())
    client = Client(hkl).client
    response = client.put(
        "/ub/test/silly_property",
        json={"h": 0, "k": 0, "l": 1},
    )
    assert response.status_code == ErrorCodes.INVALID_PROPERTY
