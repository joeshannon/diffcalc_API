from pathlib import Path
from typing import Callable, Tuple

from diffcalc.hkl.calc import HklCalculation
from fastapi import APIRouter, Body, Depends, Response

from diffcalc_API.errors.UBCalculation import (
    check_params_not_empty,
    check_property_is_valid,
)
from diffcalc_API.examples import UBCalculation as examples
from diffcalc_API.fileHandling import supplyPersist, unpickleHkl
from diffcalc_API.models.UBCalculation import (
    addOrientationParams,
    addReflectionParams,
    deleteParams,
    editOrientationParams,
    editReflectionParams,
    setLatticeParams,
)
from diffcalc_API.services import UBCalculation as service

router = APIRouter(
    prefix="/ub",
    tags=["ub"],
    dependencies=[Depends(unpickleHkl), Depends(supplyPersist)],
)


@router.get("/{name}")
async def get_UB_status(name: str, hklCalc: HklCalculation = Depends(unpickleHkl)):
    return Response(content=str(hklCalc.ubcalc), media_type="application/text")


@router.put("/{name}/reflection")
async def add_reflection(
    name: str,
    params: addReflectionParams = Body(..., example=examples.addReflection),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    service.add_reflection(name, params, hklCalc, persist)
    return {"message": f"added reflection for UB Calculation of crystal {name}"}


@router.patch("/{name}/reflection")
async def edit_reflection(
    name: str,
    params: editReflectionParams = Body(..., example=examples.editReflection),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    service.edit_reflection(name, params, hklCalc, persist)
    return {
        "message": (
            f"reflection with tag/index {params.tagOrIdx} edited to: "
            f"{hklCalc.ubcalc.get_reflection(params.tagOrIdx)}."
        )
    }


@router.delete("/{name}/reflection")
async def delete_reflection(
    name: str,
    params: deleteParams = Body(..., example={"tagOrIdx": "refl1"}),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    service.delete_reflection(name, params.tagOrIdx, hklCalc, persist)
    return {"message": f"reflection with tag/index {params.tagOrIdx} deleted."}


@router.put("/{name}/orientation")
async def add_orientation(
    name: str,
    params: addOrientationParams = Body(..., example=examples.addOrientation),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    service.add_orientation(name, params, hklCalc, persist)
    return {"message": f"added orientation for UB Calculation of crystal {name}"}


@router.patch("/{name}/orientation")
async def edit_orientation(
    name: str,
    params: editOrientationParams = Body(..., example=examples.editOrientation),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    service.edit_orientation(name, params, hklCalc, persist)
    return {
        "message": (
            f"orientation with tag/index {params.tagOrIdx} edited to: "
            f"{hklCalc.ubcalc.get_orientation(params.tagOrIdx)}."
        )
    }


@router.delete("/{name}/orientation")
async def delete_orientation(
    name: str,
    params: deleteParams = Body(..., example={"tagOrIdx": "plane"}),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    service.delete_orientation(name, params.tagOrIdx, hklCalc, persist)
    return {"message": f"reflection with tag or index {params.tagOrIdx} deleted."}


@router.patch("/{name}/lattice")
async def set_lattice(
    name: str,
    params: setLatticeParams = Body(example=examples.setLattice),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
    _=Depends(check_params_not_empty),
):
    service.set_lattice(name, params, hklCalc, persist)
    return {"message": f"lattice has been set for UB calculation of crystal {name}"}


@router.patch("/{name}/{property}")
async def modify_property(
    name: str,
    property: str,
    targetValue: Tuple[float, float, float] = Body(..., example=[1, 0, 0]),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
    _=Depends(check_property_is_valid),
):
    service.modify_property(name, property, targetValue, hklCalc, persist)
    return {"message": f"{property} has been set for UB calculation of crystal {name}"}
