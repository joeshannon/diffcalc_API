from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from diffcalc_API.errors.hkl import InvalidSolutionBoundsError
from diffcalc_API.models.hkl import SolutionConstraints
from diffcalc_API.models.ub import HklModel, PositionModel
from diffcalc_API.services import hkl as service
from diffcalc_API.stores.protocol import HklCalcStore, get_store

router = APIRouter(prefix="/hkl", tags=["hkl"])


@router.get("/{name}/UB")
async def calculate_ub(
    name: str,
    tag1: Optional[str] = Query(default=None, example="refl1"),
    idx1: Optional[int] = Query(default=None),
    tag2: Optional[str] = Query(default=None, example="plane"),
    idx2: Optional[int] = Query(default=None),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    content = await service.calculate_ub(
        name, store, collection, tag1, idx1, tag2, idx2
    )
    return {"payload": content}


@router.get("/{name}/position/lab")
async def lab_position_from_miller_indices(
    name: str,
    miller_indices: HklModel = Depends(),
    wavelength: float = Query(..., example=1.0),
    axes: Optional[List[str]] = Query(default=None, example=["mu", "nu", "phi"]),
    low_bound: Optional[List[float]] = Query(default=None, example=[0.0, 0.0, -90.0]),
    high_bound: Optional[List[float]] = Query(default=None, example=[90.0, 90.0, 90.0]),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    solutionConstraints = SolutionConstraints(axes, low_bound, high_bound)
    if not solutionConstraints.valid:
        raise InvalidSolutionBoundsError(solutionConstraints.msg)

    positions = await service.lab_position_from_miller_indices(
        name,
        miller_indices,
        wavelength,
        solutionConstraints,
        store,
        collection,
    )

    return {"payload": positions}


@router.get("/{name}/position/hkl")
async def miller_indices_from_lab_position(
    name: str,
    pos: PositionModel = Depends(),
    wavelength: float = Query(..., example=1.0),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    hkl = await service.miller_indices_from_lab_position(
        name, pos, wavelength, store, collection
    )
    return {"payload": hkl}


@router.get("/{name}/scan/hkl")
async def scan_hkl(
    name: str,
    start: List[float] = Query(..., example=[1, 0, 1]),
    stop: List[float] = Query(..., example=[2, 0, 2]),
    inc: List[float] = Query(..., example=[0.1, 0, 0.1]),
    wavelength: float = Query(..., example=1),
    axes: Optional[List[str]] = Query(default=None, example=["mu", "nu", "phi"]),
    low_bound: Optional[List[float]] = Query(default=None, example=[0.0, 0.0, -90.0]),
    high_bound: Optional[List[float]] = Query(default=None, example=[90.0, 90.0, 90.0]),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    solutionConstraints = SolutionConstraints(axes, low_bound, high_bound)
    if not solutionConstraints.valid:
        raise InvalidSolutionBoundsError(solutionConstraints.msg)

    scan_results = await service.scan_hkl(
        name,
        start,
        stop,
        inc,
        wavelength,
        solutionConstraints,
        store,
        collection,
    )
    return {"payload": scan_results}


@router.get("/{name}/scan/wavelength")
async def scan_wavelength(
    name: str,
    start: float = Query(..., example=1.0),
    stop: float = Query(..., example=2.0),
    inc: float = Query(..., example=0.2),
    hkl: HklModel = Depends(),
    axes: Optional[List[str]] = Query(default=None, example=["mu", "nu", "phi"]),
    low_bound: Optional[List[float]] = Query(default=None, example=[0.0, 0.0, -90.0]),
    high_bound: Optional[List[float]] = Query(default=None, example=[90.0, 90.0, 90.0]),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    solutionConstraints = SolutionConstraints(axes, low_bound, high_bound)
    if not solutionConstraints.valid:
        raise InvalidSolutionBoundsError(solutionConstraints.msg)

    scan_results = await service.scan_wavelength(
        name, start, stop, inc, hkl, solutionConstraints, store, collection
    )
    return {"payload": scan_results}


@router.get("/{name}/scan/{constraint}")
async def scan_constraint(
    name: str,
    constraint: str,
    start: float = Query(..., example=1),
    stop: float = Query(..., example=4),
    inc: float = Query(..., example=1),
    hkl: HklModel = Depends(),
    wavelength: float = Query(..., example=1.0),
    axes: Optional[List[str]] = Query(default=None, example=["mu", "nu", "phi"]),
    low_bound: Optional[List[float]] = Query(default=None, example=[0.0, 0.0, -90.0]),
    high_bound: Optional[List[float]] = Query(default=None, example=[90.0, 90.0, 90.0]),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    solutionConstraints = SolutionConstraints(axes, low_bound, high_bound)
    if not solutionConstraints.valid:
        raise InvalidSolutionBoundsError(solutionConstraints.msg)

    scan_results = await service.scan_constraint(
        name,
        constraint,
        start,
        stop,
        inc,
        hkl,
        wavelength,
        solutionConstraints,
        store,
        collection,
    )

    return {"payload": scan_results}
