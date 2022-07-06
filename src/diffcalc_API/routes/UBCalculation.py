import json
from typing import Optional, Tuple

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.geometry import Position
from fastapi import APIRouter, Body, Depends, HTTPException, Query

from diffcalc_API.models.UBCalculation import (
    addOrientationParams,
    addReflectionParams,
    setLatticeParams,
)
from diffcalc_API.utils import VectorProperties, pickleHkl, unpickleHkl

router = APIRouter(prefix="/update/ub", tags=["ub"])


@router.put("/{name}/lattice")
async def set_lattice(
    name: str,
    params: setLatticeParams = Body(example={"a": 4.913, "c": 5.405}),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    hkl.ubcalc.set_lattice(name=name, **params.dict())
    pickleHkl(hkl, name)
    return {"message": f"lattice set for UB calculation of crystal {name}"}


@router.put("/{name}/{property}")
async def modify_property(
    name: str,
    property: str,
    targetValue: Tuple[float, float, float] = Body(..., example=[1, 0, 0]),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    if property not in VectorProperties:
        raise HTTPException(
            status_code=401,
            detail=f"invalid property. Choose one of: {VectorProperties}",
        )

    try:
        setattr(hkl.ubcalc, property, targetValue)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"something happened: {e}")

    pickleHkl(hkl, name)
    return {"message": f"{property} set for UB calculation of crystal {name}"}


@router.put("/{name}/add/reflection")
async def add_reflection(
    name: str,
    params: addReflectionParams = Body(
        ...,
        example={
            "hkl": [0, 0, 1],
            "position": [7.31, 0.0, 10.62, 0, 0.0, 0],
            "energy": 12.39842,
            "tag": "refl1",
        },
    ),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    try:
        hkl.ubcalc.add_reflection(
            params.hkl,
            Position(*params.position),
            params.energy,
            params.tag,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"something happened: {e}")

    pickleHkl(hkl, name)
    return {"message": f"added reflection for UB Calculation of crystal {name}"}


@router.put("/{name}/add/orientation")
async def add_orientation(
    name: str,
    params: addOrientationParams = Body(
        ...,
        example={
            "hkl": [0, 1, 0],
            "xyz": [0, 1, 0],
            "tag": "plane",
        },
    ),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    position = Position(*params.position) if params.position else None

    try:
        hkl.ubcalc.add_orientation(
            params.hkl,
            params.xyz,
            position,
            params.tag,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"something happened: {e}")

    pickleHkl(hkl, name)
    return {"message": f"added orientation for UB Calculation of crystal {name}"}


@router.get("/{name}/UB")
async def calculate_UB(
    name: str,
    firstTag: Optional[str] = Query(default=None, example="refl1"),
    secondTag: Optional[str] = Query(default=None, example="plane"),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    hkl.ubcalc.calc_ub(firstTag, secondTag)

    pickleHkl(hkl, name)
    return json.dumps(np.round(hkl.ubcalc.UB, 6).tolist())
