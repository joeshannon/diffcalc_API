import json
from typing import Optional, Tuple, Union

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.geometry import Position
from fastapi import APIRouter, Body, Depends, HTTPException, Query

from diffcalc_API.models.UBCalculation import (
    addOrientationParams,
    addReflectionParams,
    editOrientationParams,
    editReflectionParams,
    setLatticeParams,
)
from diffcalc_API.utils import VectorProperties, pickleHkl, unpickleHkl

router = APIRouter(prefix="/ub", tags=["ub"])


@router.put("/{name}/reflection")
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


@router.put("/{name}/orientation")
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


@router.patch("/{name}/lattice")
async def set_lattice(
    name: str,
    params: setLatticeParams = Body(example={"a": 4.913, "c": 5.405}),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    hkl.ubcalc.set_lattice(name=name, **params.dict())
    pickleHkl(hkl, name)
    return {"message": f"lattice set for UB calculation of crystal {name}"}


@router.patch("/{name}/reflection")
async def edit_reflection(
    name: str,
    params: editReflectionParams = Body(
        ...,
        example={
            "energy": 12.45,
            "tagOrIdx": "refl1",
        },
    ),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    reflection = hkl.ubcalc.get_reflection(params.tagOrIdx)

    hkl.ubcalc.edit_reflection(
        params.tagOrIdx,
        params.hkl if params.hkl else (reflection.h, reflection.k, reflection.l),
        Position(params.position) if params.position else reflection.pos,
        params.energy if params.energy else reflection.energy,
        params.tagOrIdx if isinstance(params.tagOrIdx, str) else None,
    )
    pickleHkl(hkl, name)
    return {
        "message": (
            f"reflection edited to: {hkl.ubcalc.get_reflection(params.tagOrIdx)}."
        )
    }


@router.patch("/{name}/orientation")
async def edit_orientation(
    name: str,
    params: editOrientationParams = Body(
        ...,
        example={
            "hkl": (0, 1, 0),
            "tagOrIdx": "plane",
        },
    ),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    orientation = hkl.ubcalc.get_orientation(params.tagOrIdx)

    hkl.ubcalc.edit_orientation(
        params.tagOrIdx,
        params.hkl if params.hkl else (orientation.h, orientation.k, orientation.l),
        params.xyz if params.xyz else (orientation.x, orientation.y, orientation.z),
        Position(params.position) if params.position else orientation.pos,
        params.tagOrIdx if isinstance(params.tagOrIdx, str) else None,
    )
    pickleHkl(hkl, name)
    return {
        "message": (
            f"orientation edited to: {hkl.ubcalc.get_orientation(params.tagOrIdx)}."
        )
    }


@router.patch("/{name}/{property}")
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


@router.delete("/{name}/reflection")
async def delete_reflection(
    name: str,
    tagOrIdx: Union[str, int] = Body(..., example="refl1"),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    hkl.ubcalc.del_reflection(tagOrIdx)
    pickleHkl(hkl, name)
    return {"message": f"reflection with tag or index {tagOrIdx} deleted."}


@router.delete("/{name}/orientation")
async def delete_orientation(
    name: str,
    tagOrIdx: Union[str, int] = Body(..., example="plane"),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    hkl.ubcalc.del_orientation(tagOrIdx)
    pickleHkl(hkl, name)
    return {"message": f"reflection with tag or index {tagOrIdx} deleted."}
