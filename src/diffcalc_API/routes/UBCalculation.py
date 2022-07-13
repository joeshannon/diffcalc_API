from pathlib import Path
from typing import Callable, Tuple, Union

from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.geometry import Position
from fastapi import APIRouter, Body, Depends, Response

from diffcalc_API.errors.UBCalculation import (
    check_params_not_empty,
    check_property_is_valid,
    get_orientation,
    get_reflection,
)
from diffcalc_API.fileHandling import supplyPersist, unpickleHkl
from diffcalc_API.models.UBCalculation import (
    addOrientationParams,
    addReflectionParams,
    deleteParams,
    editOrientationParams,
    editReflectionParams,
    setLatticeParams,
)

router = APIRouter(prefix="/ub", tags=["ub"])


@router.get("/{name}")
async def get_UB_status(name: str, hklCalc: HklCalculation = Depends(unpickleHkl)):
    return Response(content=str(hklCalc.ubcalc), media_type="application/text")


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
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    hklCalc.ubcalc.add_reflection(
        params.hkl,
        Position(*params.position),
        params.energy,
        params.tag,
    )

    persist(hklCalc, name)
    return {
        "message": (
            f"added reflection for UB Calculation of crystal {name}. "
            f"Reflist is: {hklCalc.ubcalc.reflist.reflections}"
        )
    }


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
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    position = Position(*params.position) if params.position else None

    hklCalc.ubcalc.add_orientation(
        params.hkl,
        params.xyz,
        position,
        params.tag,
    )

    persist(hklCalc, name)
    return {"message": f"added orientation for UB Calculation of crystal {name}"}


@router.patch("/{name}/lattice")
async def set_lattice(
    name: str,
    params: setLatticeParams = Body(example={"a": 4.913, "c": 5.405}),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
    _=Depends(check_params_not_empty),
):
    hklCalc.ubcalc.set_lattice(name=name, **params.dict())
    persist(hklCalc, name)
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
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    reflection = get_reflection(hklCalc, params.tagOrIdx)
    hklCalc.ubcalc.edit_reflection(
        params.tagOrIdx,
        params.hkl if params.hkl else (reflection.h, reflection.k, reflection.l),
        Position(params.position) if params.position else reflection.pos,
        params.energy if params.energy else reflection.energy,
        params.tagOrIdx if isinstance(params.tagOrIdx, str) else None,
    )
    persist(hklCalc, name)
    return {
        "message": (
            f"reflection edited to: {hklCalc.ubcalc.get_reflection(params.tagOrIdx)}."
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
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    orientation = get_orientation(hklCalc, params.tagOrIdx)

    hklCalc.ubcalc.edit_orientation(
        params.tagOrIdx,
        params.hkl if params.hkl else (orientation.h, orientation.k, orientation.l),
        params.xyz if params.xyz else (orientation.x, orientation.y, orientation.z),
        Position(params.position) if params.position else orientation.pos,
        params.tagOrIdx if isinstance(params.tagOrIdx, str) else None,
    )
    persist(hklCalc, name)
    return {
        "message": (
            f"orientation edited to: {hklCalc.ubcalc.get_orientation(params.tagOrIdx)}."
        )
    }


@router.patch("/{name}/{property}")
async def modify_property(
    name: str,
    property: str,
    targetValue: Tuple[float, float, float] = Body(..., example=[1, 0, 0]),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
    _=Depends(check_property_is_valid),
):
    setattr(hklCalc.ubcalc, property, targetValue)
    persist(hklCalc, name)

    return {"message": f"{property} set for UB calculation of crystal {name}"}


@router.delete("/{name}/reflection")
async def delete_reflection(
    name: str,
    params: deleteParams = Body(..., example={"tagOrIdx": "refl1"}),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    _ = get_reflection(hklCalc, params.tagOrIdx)
    hklCalc.ubcalc.del_reflection(params.tagOrIdx)
    persist(hklCalc, name)

    return {"message": f"reflection with tag or index {params.tagOrIdx} deleted."}


@router.delete("/{name}/orientation")
async def delete_orientation(
    name: str,
    params: deleteParams = Body(..., example={"tagOrIdx": "plane"}),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    _ = get_orientation(hklCalc, params.tagOrIdx)
    hklCalc.ubcalc.del_orientation(params.tagOrIdx)
    persist(hklCalc, name)

    return {"message": f"reflection with tag or index {params.tagOrIdx} deleted."}
