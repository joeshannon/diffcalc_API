from typing import Optional, Tuple, Union

from fastapi import APIRouter, Depends, Query

from diffcalc_API.services import hkl as service
from diffcalc_API.stores.protocol import HklCalcStore, get_store

router = APIRouter(prefix="/hkl", tags=["hkl"])


SingleConstraint = Union[Tuple[str, float], str]
PositionType = Tuple[float, float, float]


@router.get("/{name}/UB")
async def calculate_ub(
    name: str,
    first_tag: Optional[Union[int, str]] = Query(default=None, example="refl1"),
    second_tag: Optional[Union[int, str]] = Query(default=None, example="plane"),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    content = await service.calculate_ub(name, first_tag, second_tag, store, collection)
    return {"payload": content}


@router.get("/{name}/position/lab")
async def lab_position_from_miller_indices(
    name: str,
    miller_indices: Tuple[float, float, float] = Query(example=[0, 0, 1]),
    wavelength: float = Query(..., example=1.0),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    positions = await service.lab_position_from_miller_indices(
        name, miller_indices, wavelength, store, collection
    )

    return {"payload": positions}


@router.get("/{name}/position/hkl")
async def miller_indices_from_lab_position(
    name: str,
    pos: Tuple[float, float, float, float, float, float] = Query(
        ..., example=[7.31, 0, 10.62, 0, 0, 0]
    ),
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
    start: PositionType = Query(..., example=(1, 0, 1)),
    stop: PositionType = Query(..., example=(2, 0, 2)),
    inc: PositionType = Query(..., example=(0.1, 0, 0.1)),
    wavelength: float = Query(..., example=1),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    scan_results = await service.scan_hkl(
        name, start, stop, inc, wavelength, store, collection
    )
    return {"payload": scan_results}


@router.get("/{name}/scan/wavelength")
async def scan_wavelength(
    name: str,
    start: float = Query(..., example=1.0),
    stop: float = Query(..., example=2.0),
    inc: float = Query(..., example=0.2),
    hkl: PositionType = Query(..., example=(1, 0, 1)),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    scan_results = await service.scan_wavelength(
        name, start, stop, inc, hkl, store, collection
    )
    return {"payload": scan_results}


@router.get("/{name}/scan/{constraint}")
async def scan_constraint(
    name: str,
    constraint: str,
    start: float = Query(..., example=1),
    stop: float = Query(..., example=4),
    inc: float = Query(..., example=1),
    hkl: PositionType = Query(..., example=(1, 0, 1)),
    wavelength: float = Query(..., example=1.0),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    scan_results = await service.scan_constraint(
        name, constraint, start, stop, inc, hkl, wavelength, store, collection
    )

    return {"payload": scan_results}
