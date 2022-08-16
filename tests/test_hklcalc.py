import ast

import numpy as np
import pytest
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.hkl.geometry import Position
from diffcalc.ub.calc import UBCalculation
from fastapi.testclient import TestClient

from diffcalc_API.errors.hkl import ErrorCodes
from diffcalc_API.server import app
from diffcalc_API.stores.protocol import HklCalcStore, get_store
from tests.conftest import FakeHklCalcStore

dummy_hkl = HklCalculation(UBCalculation(name="dummy"), Constraints())

dummy_hkl.ubcalc.set_lattice("SiO2", 4.913, 5.405)
dummy_hkl.ubcalc.n_hkl = (1, 0, 0)
dummy_hkl.ubcalc.add_reflection(
    (0, 0, 1), Position(7.31, 0, 10.62, 0, 0, 0), 12.39842, "refl1"
)
dummy_hkl.ubcalc.add_orientation((0, 1, 0), (0, 1, 0), None, "plane")
dummy_hkl.ubcalc.calc_ub("refl1", "plane")

dummy_hkl.constraints = Constraints({"qaz": 0, "alpha": 0, "eta": 0})


def dummy_get_store() -> HklCalcStore:
    return FakeHklCalcStore(dummy_hkl)


@pytest.fixture()
def client() -> TestClient:
    app.dependency_overrides[get_store] = dummy_get_store

    return TestClient(app)


def test_miller_indices_stay_the_same_after_transformation(client: TestClient):
    lab_positions = client.get(
        "/hkl/test/position/lab",
        params={"miller_indices": [0, 0, 1], "wavelength": 1},
    )

    assert lab_positions.status_code == 200
    possible_positions = lab_positions.json()["payload"]

    for pos in possible_positions:
        miller_positions = client.get(
            "/hkl/test/position/hkl",
            params={
                "pos": [
                    pos["mu"],
                    pos["delta"],
                    pos["nu"],
                    pos["eta"],
                    pos["chi"],
                    pos["phi"],
                ],
                "wavelength": 1,
            },
        )

        assert miller_positions.status_code == 200
        assert np.all(
            np.round(miller_positions.json()["payload"], 8) == np.array([0, 0, 1])
        )


def test_scan_hkl(
    client: TestClient,
):
    lab_positions = client.get(
        "/hkl/test/scan/hkl",
        params={
            "start": [1, 0, 1],
            "stop": [2, 0, 2],
            "inc": [0.5, 0, 0.5],
            "wavelength": 1,
        },
    )
    scan_results = lab_positions.json()["payload"]

    assert lab_positions.status_code == 200
    assert len(scan_results.keys()) == 9


def test_scan_wavelength(
    client: TestClient,
):
    lab_positions = client.get(
        "/hkl/test/scan/wavelength",
        params={
            "start": 1,
            "stop": 2,
            "inc": 0.5,
            "hkl": [1, 0, 1],
        },
    )
    scan_results = lab_positions.json()["payload"]

    assert lab_positions.status_code == 200
    assert len(scan_results.keys()) == 3


def test_scan_constraint(
    client: TestClient,
):
    lab_positions = client.get(
        "/hkl/test/scan/alpha",
        params={
            "start": 1,
            "stop": 2,
            "inc": 0.5,
            "hkl": [1, 0, 1],
            "wavelength": 1.0,
        },
    )
    scan_results = lab_positions.json()["payload"]

    assert lab_positions.status_code == 200
    assert len(scan_results.keys()) == 3


def test_invalid_scans(client: TestClient):
    invalid_miller_indices = client.get(
        "/hkl/test/scan/hkl",
        params={
            "start": [0, 0, 0],
            "stop": [1, 0, 1],
            "inc": [0.5, 0, 0.5],
            "wavelength": 1,
        },
    )

    assert invalid_miller_indices.status_code == ErrorCodes.INVALID_MILLER_INDICES

    invalid_wavelength_scan = client.get(
        "/hkl/test/scan/wavelength",
        params={
            "start": 1,
            "stop": 2,
            "inc": -0.5,
            "hkl": [1, 0, 1],
        },
    )

    assert invalid_wavelength_scan.status_code == ErrorCodes.INVALID_SCAN_BOUNDS


def test_calc_ub(client: TestClient):
    response = client.get(
        "/hkl/test/UB", params={"first_tag": "refl1", "second_tag": "plane"}
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


def test_calc_ub_fails_when_incorrect_tags(client: TestClient):
    response = client.get(
        "/hkl/test/UB", params={"first_tag": "one", "second_tag": "two"}
    )

    assert response.status_code == 400
