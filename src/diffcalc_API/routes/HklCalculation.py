from pathlib import Path
from typing import Callable, Optional, Tuple, Union

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from fastapi import APIRouter, Depends, Query, Response

from diffcalc_API.fileHandling import supplyPersist, unpickleHkl
from diffcalc_API.services import HklCalculation as service

router = APIRouter(
    prefix="/calculate", tags=["hkl"], dependencies=[Depends(unpickleHkl)]
)


singleConstraintType = Union[Tuple[str, float], str]
positionType = Tuple[float, float, float]


@router.get("/{name}/UB")
async def calculate_UB(
    name: str,
    firstTag: Optional[Union[int, str]] = Query(default=None, example="refl1"),
    secondTag: Optional[Union[int, str]] = Query(default=None, example="plane"),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    service.calculate_UB(name, firstTag, secondTag, hklCalc, persist)
    return Response(
        content=str(np.round(hklCalc.ubcalc.UB, 6)), media_type="application/text"
    )


@router.get("/{name}/position/lab")
async def lab_position_from_miller_indices(
    name: str,
    millerIndices: Tuple[float, float, float] = Query(example=[0, 0, 1]),
    wavelength: float = Query(..., example=1.0),
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    positions = service.lab_position_from_miller_indices(
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
    hkl = service.miller_indices_from_lab_position(pos, wavelength, hklCalc)
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
    scanResults = service.scan_hkl(start, stop, inc, wavelength, hklCalc)
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
    scanResults = service.scan_wavelength(start, stop, inc, hkl, hklCalc)
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
    scanResults = service.scan_constraint(
        constraint, start, stop, inc, hkl, wavelength, hklCalc
    )

    return {"payload": scanResults}
