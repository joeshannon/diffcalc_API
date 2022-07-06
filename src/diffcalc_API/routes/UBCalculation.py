import json
from typing import Optional, Tuple, Union

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.geometry import Position
from diffcalc.ub.calc import UBCalculation
from fastapi import APIRouter, Body, Depends, HTTPException

from diffcalc_API.models.UBCalculation import (
    addOrientationParams,
    addReflectionParams,
    setLatticeParams,
)
from diffcalc_API.utils import OpenPickle, VectorProperties, makePickleFile, returnHkl

UB = OpenPickle("ub")
router = APIRouter(prefix="/ub", tags=["ub"])


@router.post("/create/{name}")
async def make_calc(name: str):
    calc = UBCalculation(name=name)
    fp = makePickleFile(name, "ub")

    calc.pickle(fp)
    return {"message": f"file created at {fp}"}


@router.put("/update/{name}/lattice")
async def set_lattice(
    name: str,
    setLatticeParams: setLatticeParams = Body(example={"a": 4.913, "c": 5.405}),
    calc: UBCalculation = Depends(UB),
    hkl: Union[HklCalculation, None] = Depends(returnHkl),
):
    try:
        calc.set_lattice(name=name, **setLatticeParams.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"something happened: {e}")

    pickleFile = makePickleFile(name, "ub")
    calc.pickle(pickleFile)

    return {"message": f"lattice set for file at {pickleFile}"}


@router.put("/update/{name}/{property}")
async def modify_property(
    name: str,
    property: str,
    targetValue: Tuple[float, float, float] = Body(..., example=[1, 0, 0]),
    calc: UBCalculation = Depends(UB),
):
    if property not in VectorProperties:
        raise HTTPException(
            status_code=401,
            detail=f"invalid property. Choose one of: {VectorProperties}",
        )

    try:
        setattr(calc, property, targetValue)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"something happened: {e}")

    pickleFile = makePickleFile(name, "ub")
    calc.pickle(pickleFile)
    return {"message": f"{property} updated for file at {pickleFile}"}


@router.put("/update/{name}/add/reflection")
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
    calc: UBCalculation = Depends(UB),
):
    try:
        calc.add_reflection(
            params.hkl,
            Position(*params.position),
            params.energy,
            params.tag,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"something happened: {e}")

    pickleFile = makePickleFile(name, "ub")
    calc.pickle(pickleFile)
    return {"message": f"added reflection for file at {pickleFile}"}


@router.put("/update/{name}/add/orientation")
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
    calc: UBCalculation = Depends(UB),
):
    position = Position(*params.position) if params.position else None

    try:
        calc.add_orientation(
            params.hkl,
            params.xyz,
            position,
            params.tag,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"something happened: {e}")

    pickleFile = makePickleFile(name, "ub")
    calc.pickle(pickleFile)
    return {"message": f"added orientation for file at {pickleFile}"}


@router.get("/update/{name}/UB")
async def calculate_UB(
    name: str,
    firstTag: Optional[str] = None,
    secondTag: Optional[str] = None,
    calc: UBCalculation = Depends(UB),
):
    calc.calc_ub(firstTag, secondTag)

    calc.pickle(makePickleFile(name, "ub"))
    return json.dumps(np.round(calc.UB, 6).tolist())
