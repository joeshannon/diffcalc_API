from typing import Tuple, Union

from diffcalc.hkl.calc import HklCalculation
from fastapi import APIRouter, Depends, Query

from diffcalc_API.controllers import HklCalculation as controller
from diffcalc_API.fileHandling import unpickleHkl

router = APIRouter(
    prefix="/calculate", tags=["hkl"], dependencies=[Depends(unpickleHkl)]
)


singleConstraintType = Union[Tuple[str, float], str]
positionType = Tuple[float, float, float]


@router.get("/{name}/position/lab")
async def lab_position_from_miller_indices(
    name: str,
    millerIndices: Tuple[float, float, float] = Query(example=[0, 0, 1]),
    wavelength: float = Query(..., example=1.0),
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    positions = controller.lab_position_from_miller_indices(
        millerIndices, wavelength, hklCalc
    )

    return {"payload": positions}


@router.get("/{name}/position/hkl")
async def miller_indices_from_lab_position(
    name: str,
    pos: Tuple[float, float, float, float, float, float] = Query(
        ..., example=[7.31, 0, 10.62, 0, 0, 0]
    ),
    wavelength: float = Query(..., example=1.0),
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    hkl = controller.miller_indices_from_lab_position(pos, wavelength, hklCalc)
    return {"payload": hkl}


@router.get("/{name}/scan/hkl")
async def scan_hkl(
    name: str,
    start: positionType = Query(..., example=(1, 0, 1)),
    stop: positionType = Query(..., example=(2, 0, 2)),
    inc: positionType = Query(..., example=(0.1, 0, 0.1)),
    wavelength: float = Query(..., example=1),
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    scanResults = controller.scan_hkl(start, stop, inc, wavelength, hklCalc)
    return {"payload": scanResults}


@router.get("/{name}/scan/wavelength")
async def scan_wavelength(
    name: str,
    start: float = Query(..., example=1.0),
    stop: float = Query(..., example=2.0),
    inc: float = Query(..., example=0.2),
    hkl: positionType = Query(..., example=(1, 0, 1)),
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    scanResults = controller.scan_wavelength(start, stop, inc, hkl, hklCalc)
    return {"payload": scanResults}


@router.get("/{name}/scan/{constraint}")
async def scan_constraint(
    name: str,
    constraint: str,
    start: float = Query(..., example=1),
    stop: float = Query(..., example=4),
    inc: float = Query(..., example=1),
    hkl: positionType = Query(..., example=(1, 0, 1)),
    wavelength: float = Query(..., example=1.0),
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    scanResults = controller.scan_constraint(
        constraint, start, stop, inc, hkl, wavelength, hklCalc
    )

    return {"payload": scanResults}
