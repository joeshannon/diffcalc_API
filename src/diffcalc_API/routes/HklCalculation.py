from itertools import product
from typing import Dict, List, Tuple, Union

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.geometry import Position
from fastapi import APIRouter, Depends, Query

from diffcalc_API.errors.HklCalculation import (
    check_valid_miller_indices,
    check_valid_start_stop_inc,
    get_positions,
)
from diffcalc_API.fileHandling import unpickleHkl
from diffcalc_API.models.HklCalculation import positionType

router = APIRouter(prefix="/calculate", tags=["hkl"])


singleConstraintType = Union[Tuple[str, float], str]


@router.get("/{name}/position/lab")
async def lab_position_from_miller_indices(
    name: str,
    millerIndices: Tuple[float, float, float] = Query(example=[0, 0, 1]),
    wavelength: float = Query(..., example=1.0),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    _=Depends(check_valid_miller_indices),
):
    allPositions = get_positions(hklCalc, millerIndices, wavelength)

    return {"payload": allPositions}


@router.get("/{name}/position/hkl")
async def miller_indices_from_lab_position(
    name: str,
    pos: Tuple[float, float, float, float, float, float] = Query(
        ..., example=[7.31, 0, 10.62, 0, 0, 0]
    ),
    wavelength: float = Query(..., example=1.0),
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    hklPosition = hklCalc.get_hkl(Position(*pos), wavelength)
    return {"payload": tuple(np.round(hklPosition, 16))}


def generate_axis(start: float, stop: float, inc: float):
    check_valid_start_stop_inc(start, stop, inc)
    return np.arange(start, stop + inc, inc)


@router.get("/{name}/scan/hkl")
async def scan_hkl(
    name: str,
    start: positionType = Query(..., example=(1, 0, 1)),
    stop: positionType = Query(..., example=(2, 0, 2)),
    inc: positionType = Query(..., example=(0.1, 0, 0.1)),
    wavelength: float = Query(..., example=1),
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    valueOfAxes = [
        generate_axis(start[i], stop[i], inc[i]) if inc[i] != 0 else [0]
        for i in range(3)
    ]

    results = {}

    for h, k, l in product(*valueOfAxes):
        allPositions = get_positions(hklCalc, (h, k, l), wavelength)
        results[f"({h}, {k}, {l})"] = combine_lab_position_results(allPositions)

    return {"payload": results}


@router.get("/{name}/scan/wavelength")
async def scan_wavelength(
    name: str,
    start: float = Query(..., example=1.0),
    stop: float = Query(..., example=2.0),
    inc: float = Query(..., example=0.2),
    hkl: positionType = Query(..., example=(1, 0, 1)),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    _=Depends(check_valid_start_stop_inc),
):
    wavelengths = np.arange(start, stop + inc, inc)
    result = {}

    for wavelength in wavelengths:
        allPositions = get_positions(hklCalc, hkl, wavelength)
        result[f"{wavelength}"] = combine_lab_position_results(allPositions)

    return {"payload": result}


@router.get("/{name}/scan/{constraint}")
async def scan_constraint(
    name: str,
    variable: str,
    start: float = Query(..., example=1),
    stop: float = Query(..., example=4),
    inc: float = Query(..., example=1),
    hkl: positionType = Query(..., example=(1, 0, 1)),
    wavelength: float = Query(..., example=1.0),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    _=Depends(check_valid_start_stop_inc),
):
    result = {}
    for value in np.arange(start, stop + inc, inc):
        setattr(hklCalc, variable, value)
        allPositions = get_positions(hklCalc, hkl, wavelength)
        result[f"{value}"] = combine_lab_position_results(allPositions)

    return {"payload": result}


def combine_lab_position_results(positions: List[Tuple[Position, Dict[str, float]]]):
    result = []

    for position in positions:
        result.append({**position[0].asdict, **position[1]})

    return result
