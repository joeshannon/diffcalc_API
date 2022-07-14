from typing import Tuple

from fastapi import APIRouter, Body, Depends, Response

from diffcalc_API.errors.UBCalculation import (
    check_params_not_empty,
    check_property_is_valid,
)
from diffcalc_API.examples import UBCalculation as examples
from diffcalc_API.fileHandling import HklCalcRepo, get_repo
from diffcalc_API.models.UBCalculation import (
    addOrientationParams,
    addReflectionParams,
    deleteParams,
    editOrientationParams,
    editReflectionParams,
    setLatticeParams,
)
from diffcalc_API.services import UBCalculation as service

router = APIRouter(prefix="/ub", tags=["ub"])


@router.get("/{name}")
async def get_UB(name: str, repo: HklCalcRepo = Depends(get_repo)):
    content = await service.get_UB(name, repo)
    return Response(content=content, media_type="application/text")


@router.put("/{name}/reflection")
async def add_reflection(
    name: str,
    params: addReflectionParams = Body(..., example=examples.addReflection),
    repo: HklCalcRepo = Depends(get_repo),
):
    await service.add_reflection(name, params, repo)
    return {"message": f"added reflection for UB Calculation of crystal {name}"}


@router.patch("/{name}/reflection")
async def edit_reflection(
    name: str,
    params: editReflectionParams = Body(..., example=examples.editReflection),
    repo: HklCalcRepo = Depends(get_repo),
):
    await service.edit_reflection(name, params, repo)
    return {"message": f"reflection with tag/index {params.tagOrIdx} edited. "}


@router.delete("/{name}/reflection")
async def delete_reflection(
    name: str,
    params: deleteParams = Body(..., example={"tagOrIdx": "refl1"}),
    repo: HklCalcRepo = Depends(get_repo),
):
    await service.delete_reflection(name, params.tagOrIdx, repo)  # TODO Change this!
    return {"message": f"reflection with tag/index {params.tagOrIdx} deleted."}


@router.put("/{name}/orientation")
async def add_orientation(
    name: str,
    params: addOrientationParams = Body(..., example=examples.addOrientation),
    repo: HklCalcRepo = Depends(get_repo),
):
    await service.add_orientation(name, params, repo)
    return {"message": f"added orientation for UB Calculation of crystal {name}"}


@router.patch("/{name}/orientation")
async def edit_orientation(
    name: str,
    params: editOrientationParams = Body(..., example=examples.editOrientation),
    repo: HklCalcRepo = Depends(get_repo),
):
    await service.edit_orientation(name, params, repo)
    return {"message": f"orientation with tag/index {params.tagOrIdx} edited."}


@router.delete("/{name}/orientation")
async def delete_orientation(
    name: str,
    params: deleteParams = Body(..., example={"tagOrIdx": "plane"}),
    repo: HklCalcRepo = Depends(get_repo),
):
    await service.delete_orientation(name, params.tagOrIdx, repo)
    return {"message": f"reflection with tag or index {params.tagOrIdx} deleted."}


@router.patch("/{name}/lattice")
async def set_lattice(
    name: str,
    params: setLatticeParams = Body(example=examples.setLattice),
    repo: HklCalcRepo = Depends(get_repo),
    _=Depends(check_params_not_empty),
):
    await service.set_lattice(name, params, repo)
    return {"message": f"lattice has been set for UB calculation of crystal {name}"}


@router.patch("/{name}/{property}")
async def modify_property(
    name: str,
    property: str,
    targetValue: Tuple[float, float, float] = Body(..., example=[1, 0, 0]),
    repo: HklCalcRepo = Depends(get_repo),
    _=Depends(check_property_is_valid),
):
    await service.modify_property(name, property, targetValue, repo)
    return {"message": f"{property} has been set for UB calculation of crystal {name}"}
