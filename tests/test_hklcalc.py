import numpy as np
import pytest
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.hkl.geometry import Position
from diffcalc.ub.calc import UBCalculation
from fastapi.testclient import TestClient

from diffcalc_API.errors.HklCalculation import codes
from diffcalc_API.fileHandling import HklCalcRepo, get_repo
from diffcalc_API.server import app
from tests.conftest import FakeHklCalcRepo

dummyHkl = HklCalculation(UBCalculation(name="sixcircle"), Constraints())

dummyHkl.ubcalc.set_lattice("SiO2", 4.913, 5.405)
dummyHkl.ubcalc.n_hkl = (1, 0, 0)
dummyHkl.ubcalc.add_reflection(
    (0, 0, 1), Position(7.31, 0, 10.62, 0, 0, 0), 12.39842, "refl1"
)
dummyHkl.ubcalc.add_orientation((0, 1, 0), (0, 1, 0), None, "plane")
dummyHkl.ubcalc.calc_ub("refl1", "plane")

dummyHkl.constraints = Constraints({"qaz": 0, "alpha": 0, "eta": 0})


def dummy_get_repo() -> HklCalcRepo:
    return FakeHklCalcRepo(dummyHkl)


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_repo] = dummy_get_repo

    return TestClient(app)


def test_miller_indices_stay_the_same_after_transformation(client: TestClient):

    labPositions = client.get(
        "/calculate/test/position/lab",
        params={"millerIndices": [0, 0, 1], "wavelength": 1},
    )

    assert labPositions.status_code == 200
    possiblePositions = labPositions.json()["payload"]

    for pos in possiblePositions:
        millerPos = client.get(
            "/calculate/test/position/hkl",
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

        assert millerPos.status_code == 200
        assert np.all(np.round(millerPos.json()["payload"], 8) == np.array([0, 0, 1]))


def test_scan_hkl(
    client: TestClient,
):
    labPositions = client.get(
        "/calculate/test/scan/hkl",
        params={
            "start": [1, 0, 1],
            "stop": [2, 0, 2],
            "inc": [0.5, 0, 0.5],
            "wavelength": 1,
        },
    )
    scanResults = labPositions.json()["payload"]

    assert labPositions.status_code == 200
    assert len(scanResults.keys()) == 9


def test_scan_wavelength(
    client: TestClient,
):
    labPositions = client.get(
        "/calculate/test/scan/wavelength",
        params={
            "start": 1,
            "stop": 2,
            "inc": 0.5,
            "hkl": [1, 0, 1],
        },
    )
    scanResults = labPositions.json()["payload"]

    assert labPositions.status_code == 200
    assert len(scanResults.keys()) == 3


def test_scan_constraint(
    client: TestClient,
):
    labPositions = client.get(
        "/calculate/test/scan/alpha",
        params={
            "start": 1,
            "stop": 2,
            "inc": 0.5,
            "hkl": [1, 0, 1],
            "wavelength": 1.0,
        },
    )
    scanResults = labPositions.json()["payload"]

    assert labPositions.status_code == 200
    assert len(scanResults.keys()) == 3


def test_invalid_scans(client: TestClient):
    invalidMillerIndices = client.get(
        "/calculate/test/scan/hkl",
        params={
            "start": [0, 0, 0],
            "stop": [1, 0, 1],
            "inc": [0.5, 0, 0.5],
            "wavelength": 1,
        },
    )

    assert invalidMillerIndices.status_code == codes.check_valid_miller_indices

    invalidWavelengthScan = client.get(
        "/calculate/test/scan/wavelength",
        params={
            "start": 1,
            "stop": 2,
            "inc": -0.5,
            "hkl": [1, 0, 1],
        },
    )

    assert invalidWavelengthScan.status_code == codes.check_valid_scan_bounds


def test_calculate_UB(client: TestClient):
    response = client.get(
        "/calculate/test/UB", params={"firstTag": "refl1", "secondTag": "plane"}
    )
    expected_UB = (
        "[[ 1.27889  -0.        0.      ],  [-0.        1.278111  0.04057 ],"
        "  [-0.       -0.044633  1.161768]]"
    )

    assert response.status_code == 200
    assert response.text.replace("\n", ", ") == expected_UB


def test_calculate_UB_fails_when_incorrect_tags(client: TestClient):
    response = client.get(
        "/calculate/test/UB", params={"firstTag": "one", "secondTag": "two"}
    )

    assert response.status_code == codes.calculate_UB_matrix
