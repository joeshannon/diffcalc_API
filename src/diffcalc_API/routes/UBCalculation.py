from typing import Tuple

from fastapi import APIRouter, Body, Depends, Response

from diffcalc_API.errors.UBCalculation import (
    check_params_not_empty,
    check_property_is_valid,
)
from diffcalc_API.examples import UBCalculation as examples
from diffcalc_API.models.UBCalculation import (
    addOrientationParams,
    addReflectionParams,
    deleteParams,
    editOrientationParams,
    editReflectionParams,
    setLatticeParams,
)
from diffcalc_API.services import UBCalculation as service
from diffcalc_API.stores.pickling import get_store
from diffcalc_API.stores.protocol import HklCalcStore

router = APIRouter(prefix="/ub", tags=["ub"])


@router.get("/{name}")
async def get_UB(name: str, store: HklCalcStore = Depends(get_store)):
    content = await service.get_UB(name, store)
    return Response(content=content, media_type="application/text")


@router.put("/{name}/reflection")
async def add_reflection(
    name: str,
    params: addReflectionParams = Body(..., example=examples.addReflection),
    store: HklCalcStore = Depends(get_store),
):
    await service.add_reflection(name, params, store)
    return {"message": f"added reflection for UB Calculation of crystal {name}"}


@router.patch("/{name}/reflection")
async def edit_reflection(
    name: str,
    params: editReflectionParams = Body(..., example=examples.editReflection),
    store: HklCalcStore = Depends(get_store),
):
    await service.edit_reflection(name, params, store)
    return {"message": f"reflection with tag/index {params.tagOrIdx} edited. "}


@router.delete("/{name}/reflection")
async def delete_reflection(
    name: str,
    params: deleteParams = Body(..., example={"tagOrIdx": "refl1"}),
    store: HklCalcStore = Depends(get_store),
):
    await service.delete_reflection(name, params.tagOrIdx, store)  # TODO Change this!
    return {"message": f"reflection with tag/index {params.tagOrIdx} deleted."}


@router.put("/{name}/orientation")
async def add_orientation(
    name: str,
    params: addOrientationParams = Body(..., example=examples.addOrientation),
    store: HklCalcStore = Depends(get_store),
):
    await service.add_orientation(name, params, store)
    return {"message": f"added orientation for UB Calculation of crystal {name}"}


@router.patch("/{name}/orientation")
async def edit_orientation(
    name: str,
    params: editOrientationParams = Body(..., example=examples.editOrientation),
    store: HklCalcStore = Depends(get_store),
):
    await service.edit_orientation(name, params, store)
    return {"message": f"orientation with tag/index {params.tagOrIdx} edited."}


@router.delete("/{name}/orientation")
async def delete_orientation(
    name: str,
    params: deleteParams = Body(..., example={"tagOrIdx": "plane"}),
    store: HklCalcStore = Depends(get_store),
):
    await service.delete_orientation(name, params.tagOrIdx, store)
    return {"message": f"reflection with tag or index {params.tagOrIdx} deleted."}


@router.patch("/{name}/lattice")
async def set_lattice(
    name: str,
    params: setLatticeParams = Body(example=examples.setLattice),
    store: HklCalcStore = Depends(get_store),
    _=Depends(check_params_not_empty),
):
    await service.set_lattice(name, params, store)
    return {"message": f"lattice has been set for UB calculation of crystal {name}"}


@router.patch("/{name}/{property}")
async def modify_property(
    name: str,
    property: str,
    targetValue: Tuple[float, float, float] = Body(..., example=[1, 0, 0]),
    store: HklCalcStore = Depends(get_store),
    _=Depends(check_property_is_valid),
):
    await service.modify_property(name, property, targetValue, store)
    return {"message": f"{property} has been set for UB calculation of crystal {name}"}
