import ast
import math
from ast import literal_eval
from math import radians
from typing import Dict

import numpy as np
import pytest
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.hkl.geometry import Position
from diffcalc.ub.calc import UBCalculation
from diffcalc.ub.reference import Orientation, Reflection
from fastapi.testclient import TestClient

from diffcalc_api.errors.ub import (
    BothTagAndIdxProvidedError,
    ErrorCodes,
    InvalidIndexError,
    NoCrystalError,
    NoTagOrIdxProvidedError,
    NoUbMatrixError,
    ReferenceRetrievalError,
)
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


def test_get_ub_status():
    hkl = HklCalculation(UBCalculation("dummy"), Constraints())
    client = Client(hkl).client

    response = client.get("/ub/test/status")
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


def test_get_ub():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ubcalc.UB = np.identity(3)

    response = client.get("/ub/test/ub")

    assert response.status_code == 200
    assert literal_eval(response.content.decode())["payload"] == np.identity(3).tolist()


def test_get_u():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ubcalc.U = np.identity(3)

    response = client.get("/ub/test/u")

    assert response.status_code == 200
    assert literal_eval(response.content.decode())["payload"] == np.identity(3).tolist()


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


def test_get_reflection():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ref = Reflection(0.0, 1.0, 0.0, Position(7, 0, 10, 0, 0, 0), 12, "")
    ubcalc.reflist.reflections.append(ref)

    response = client.get("/ub/test/reflection?idx=1")

    assert response.status_code == 200
    assert literal_eval(response.content.decode())["payload"] == ref.asdict


def test_get_reflection_fails_for_wrong_inputs():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ref = Reflection(0.0, 1.0, 0.0, Position(7, 0, 10, 0, 0, 0), 12, "")
    ubcalc.reflist.reflections.append(ref)

    response_no_idx_or_tag = client.get("/ub/test/reflection?")
    response_both_idx_and_tag = client.get("/ub/test/reflection?idx=1&tag=two")
    response_wrong_idx = client.get("/ub/test/reflection?idx=2")
    response_wrong_tag = client.get("/ub/test/reflection?tag=two")

    def select_type(response):
        return literal_eval(response.content.decode())["type"]

    assert select_type(response_no_idx_or_tag) == str(NoTagOrIdxProvidedError)
    assert select_type(response_both_idx_and_tag) == str(BothTagAndIdxProvidedError)
    assert select_type(response_wrong_idx) == str(ReferenceRetrievalError)
    assert select_type(response_wrong_tag) == str(ReferenceRetrievalError)


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


def test_get_orientation():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    orient = Orientation(0.0, 1.0, 0.0, 1.0, 0.0, 0.0, Position(), "")
    ubcalc.orientlist.orientations.append(orient)

    response = client.get("/ub/test/orientation?idx=1")

    assert response.status_code == 200
    assert literal_eval(response.content.decode())["payload"] == orient.asdict


def test_get_orientation_fails_for_wrong_inputs():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    orient = Orientation(0.0, 1.0, 0.0, 0.0, 1.0, 0.0, Position(7, 0, 10, 0, 0, 0), "")
    ubcalc.orientlist.orientations.append(orient)

    response_no_idx_or_tag = client.get("/ub/test/orientation?")
    response_both_idx_and_tag = client.get("/ub/test/orientation?idx=1&tag=two")
    response_wrong_idx = client.get("/ub/test/orientation?idx=2")
    response_wrong_tag = client.get("/ub/test/orientation?tag=two")

    def select_type(response):
        return literal_eval(response.content.decode())["type"]

    assert select_type(response_no_idx_or_tag) == str(NoTagOrIdxProvidedError)
    assert select_type(response_both_idx_and_tag) == str(BothTagAndIdxProvidedError)
    assert select_type(response_wrong_idx) == str(ReferenceRetrievalError)
    assert select_type(response_wrong_tag) == str(ReferenceRetrievalError)


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


def test_set_miscut_with_existing_u():
    ubcalc = UBCalculation("LSMO_327_001")
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ubcalc.set_lattice("LSMO_327", "Triclinic", 3.78, 3.78, 20.1, 90.0, 90.0, 90.0)
    ubcalc.add_orientation(
        [0, 0, 1], [0, 0, 1], Position(60.0585, 0, 90.4052, 0, -29.5624, 39.1178)
    )
    ubcalc.add_orientation(
        [0, 1, 0], [0, 1, 0], Position(60.0585, 0, 90.4052, 0, -29.5624, 39.1178)
    )
    ubcalc.calc_ub()
    ubcalc.n_phi = [0.0, 1.0, 0.0]

    angle_in_rad = math.radians(11)
    rotation_axis = {"x": 0, "y": 1, "z": 0}

    client.put(
        "/ub/test/miscut?collection=B07",
        params={"angle": angle_in_rad, "add_miscut": True},
        json=rotation_axis,
    )

    get_response = client.get("/ub/test/miscut?collection=B07")
    get_response_payload = ast.literal_eval(get_response.content.decode())["payload"]

    assert get_response_payload["angle"] == 1.0540812808041131


def test_set_and_get_miscut():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    # angle = 0.85212
    # rotation_axis = {"x": -0.25142, "y": -0.96788, "z": 0.0}

    angle_in_rad = math.radians(11)
    rotation_axis = {"x": 0, "y": 1, "z": 0}

    client.put(
        "/ub/test/miscut?collection=B07",
        params={"angle": angle_in_rad, "add_miscut": False},
        json=rotation_axis,
    )

    get_response = client.get("/ub/test/miscut?collection=B07")
    get_response_payload = ast.literal_eval(get_response.content.decode())["payload"]

    assert get_response_payload["angle"] == pytest.approx(angle_in_rad)

    for key, value in get_response_payload["rotation_axis"].items():
        assert np.round(value, 5) == np.round(rotation_axis[key], 5)


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
        "/ub/test/calculate", params={"first_tag": "refl1", "second_tag": "plane"}
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
    assert np.all(
        np.round(ast.literal_eval(response.content.decode())["payload"], 5)
        == np.round(expected_ub, 5)
    )


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
    response = client.put("/ub/test/u?collection=B07", json=u_matrix.tolist())

    assert np.all(ubcalc.U == u_matrix)
    assert (
        literal_eval(response.content.decode())["message"]
        == "U matrix set for crystal test of collection B07"
    )


def test_set_ub():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ub_matrix = np.identity(3)
    response = client.put("/ub/test/ub?collection=B07", json=ub_matrix.tolist())

    assert np.all(ubcalc.UB == ub_matrix)
    assert (
        literal_eval(response.content.decode())["message"]
        == "UB matrix set for crystal test of collection B07"
    )


def test_refine_ub():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    ubcalc.set_lattice("LSMO_327", 3.78, 3.78, 20.1, 90, 90, 90)
    ubcalc.add_orientation([0, 0, 1], [1, 0, 0])
    ubcalc.add_orientation([0, 1, 0], [0, 1, 0])

    ubcalc.calc_ub()

    ubcalc.n_phi = [0.0, 1.0, 0.0]

    ubcalc.set_miscut([1.0, 0.0, 0.0], radians(3))

    ub_after_miscut = ubcalc.UB

    client.patch(
        "/ub/test/refine?collection=B07",
        json={
            "hkl": {"h": 0, "k": 0, "l": 2},
            "position": {
                "mu": 100.0,
                "delta": 0.0,
                "nu": 82.9408,
                "eta": 0.0,
                "chi": 30.31,
                "phi": 0.0,
            },
            "wavelength": 13.3109,
        },
        params={"refine_lattice": 1, "refine_u_matrix": 1},
    )

    assert np.any(ubcalc.UB != ub_after_miscut)


@pytest.mark.parametrize(
    ["url", "body", "property"],
    [
        ["/ub/test/nhkl?collection=B07", {"h": 0, "k": 0, "l": 1}, "n_hkl"],
        ["/ub/test/nphi?collection=B07", {"x": 0, "y": 0, "z": 1}, "n_phi"],
        ["/ub/test/surface/nhkl?collection=B07", {"h": 0, "k": 0, "l": 1}, "surf_nhkl"],
        ["/ub/test/surface/nphi?collection=B07", {"x": 0, "y": 0, "z": 1}, "surf_nphi"],
    ],
)
def test_get_and_set_reference_vectors_hkl(
    url: str, body: Dict[str, float], property: str
):
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client
    response_put = client.put(
        url,
        json=body,
    )

    if property.endswith("hkl"):
        body_as_array = np.array([[body["h"], body["k"], body["l"]]])
    else:
        body_as_array = np.array([[body["x"], body["y"], body["z"]]])

    assert response_put.status_code == 200
    assert np.all(getattr(ubcalc, property) == np.transpose(body_as_array))

    response_get = client.get(url)

    assert np.all(
        np.array(literal_eval(response_get.content.decode())["payload"]).T
        == body_as_array
    )


def test_get_reference_vectors_for_null_vectors():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    response = client.get("/ub/test/nphi?collection=B07")
    assert literal_eval(response.content.decode())["payload"] == [[]]


def test_calculate_vector_from_hkl_and_offset():
    ubcalc = UBCalculation()
    ubcalc.UB = np.identity(3)

    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    response = client.get(
        "/ub/test/vector?polar_angle=90.0&azimuth_angle=0.0&collection=B07",
        params={"h": 1.0, "k": 0.0, "l": 0.0},
    )

    assert response.status_code == 200
    response_miller = literal_eval(response.content.decode())["payload"]

    assert response_miller["h"] == pytest.approx(0.0)
    assert response_miller["k"] == pytest.approx(1.0)
    assert response_miller["l"] == pytest.approx(0.0)


def test_calculate_vector_from_hkl_and_offset_fails_for_no_ub_matrix():
    ubcalc = UBCalculation()

    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    response = client.get(
        "/ub/test/vector?polar_angle=90.0&azimuth_angle=0.0&collection=B07",
        params={"h": 1.0, "k": 0.0, "l": 0.0},
    )

    assert response.status_code == ErrorCodes.NO_UB_MATRIX_ERROR

    content = literal_eval(response.content.decode())

    assert content["type"] == str(NoUbMatrixError)
    assert content["message"].startswith(
        "It seems like there is no UB matrix for this record."
    )


def test_calculate_offset_from_vector_and_hkl():
    ubcalc = UBCalculation()
    ubcalc.UB = np.identity(3)
    ubcalc.set_lattice("", "Cubic", 1.0)

    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    response = client.get(
        "/ub/test/offset?h1=1.0&k1=0.0&l1=0.0&h2=0.0&k2=1.0&l2=0.0&collection=B07",
        params={"h": 0.0, "k": 1.0, "l": 0.0},
    )

    assert response.status_code == 200
    response_spherical = literal_eval(response.content.decode())["payload"]

    assert response_spherical["magnitude"] == 1.0
    assert response_spherical["azimuth_angle"] == 0.0
    assert response_spherical["polar_angle"] == 90.0


def test_calculate_offset_from_vector_and_hkl_fails_for_no_ub_matrix_or_crystal():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    response_no_ub = client.get(
        "/ub/test/offset?h1=1.0&k1=0.0&l1=0.0&h2=0.0&k2=1.0&l2=0.0&collection=B07",
        params={"h": 0.0, "k": 1.0, "l": 0.0},
    )

    assert response_no_ub.status_code == ErrorCodes.NO_UB_MATRIX_ERROR
    content_no_ub = literal_eval(response_no_ub.content.decode())
    assert content_no_ub["type"] == str(NoUbMatrixError)

    ubcalc.UB = np.identity(3)

    response_no_crystal = client.get(
        "/ub/test/offset?h1=1.0&k1=0.0&l1=0.0&h2=0.0&k2=1.0&l2=0.0&collection=B07",
        params={"h": 0.0, "k": 1.0, "l": 0.0},
    )

    assert response_no_crystal.status_code == ErrorCodes.NO_CRYSTAL_ERROR
    content_no_crystal = literal_eval(response_no_crystal.content.decode())
    assert content_no_crystal["type"] == str(NoCrystalError)


def test_hkl_solver_for_fixed_q():
    ubcalc = UBCalculation()
    ubcalc.UB = np.identity(3)

    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    response = client.get(
        "/ub/test/solve/hkl/fixed/q?"
        + "index_name=h&index_value=0.0&a=0.0&b=1.0&c=0.0&d=0.25&collection=B07",
        params={"h": 0.0, "k": 1.0, "l": 0.0},
    )

    assert response.status_code == 200

    hkl_list = literal_eval(response.content.decode())["payload"]
    assert hkl_list == [
        [0.0, 0.25, -0.9682458365518543],
        [0.0, 0.25, 0.9682458365518543],
    ]


def test_hkl_solver_for_fixed_q_fails_if_no_ub_or_invalid_index_given():
    ubcalc = UBCalculation()
    hkl = HklCalculation(ubcalc, Constraints())
    client = Client(hkl).client

    response = client.get(
        "/ub/test/solve/hkl/fixed/q?"
        + "index_name=h&index_value=0.0&a=0.0&b=1.0&c=0.0&d=0.25&collection=B07",
        params={"h": 0.0, "k": 1.0, "l": 0.0},
    )

    assert response.status_code == ErrorCodes.NO_UB_MATRIX_ERROR
    assert literal_eval(response.content.decode())["type"] == str(NoUbMatrixError)

    ubcalc.UB = np.identity(3)

    response = client.get(
        "/ub/test/solve/hkl/fixed/q?"
        + "index_name=p&index_value=0.0&a=0.0&b=1.0&c=0.0&d=0.25&collection=B07",
        params={"h": 0.0, "k": 1.0, "l": 0.0},
    )

    assert response.status_code == ErrorCodes.INVALID_INDEX_ERROR
    assert literal_eval(response.content.decode())["type"] == str(InvalidIndexError)
