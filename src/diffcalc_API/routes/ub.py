from typing import Tuple

from fastapi import APIRouter, Body, Depends, Response

from diffcalc_API.errors.ub import check_params_not_empty, check_property_is_valid
from diffcalc_API.examples import ub as examples
from diffcalc_API.models.ub import (
    AddOrientationParams,
    AddReflectionParams,
    DeleteParams,
    EditOrientationParams,
    EditReflectionParams,
    SetLatticeParams,
)
from diffcalc_API.services import ub as service
from diffcalc_API.stores.pickling import get_store
from diffcalc_API.stores.protocol import HklCalcStore

router = APIRouter(prefix="/ub", tags=["ub"])


@router.get("/{name}")
async def get_ub(name: str, store: HklCalcStore = Depends(get_store)):
    content = await service.get_ub(name, store)
    return Response(content=content, media_type="application/text")


@router.put("/{name}/reflection")
async def add_reflection(
    name: str,
    params: AddReflectionParams = Body(..., example=examples.add_reflection),
    store: HklCalcStore = Depends(get_store),
):
    await service.add_reflection(name, params, store)
    return {"message": f"added reflection for UB Calculation of crystal {name}"}


@router.patch("/{name}/reflection")
async def edit_reflection(
    name: str,
    params: EditReflectionParams = Body(..., example=examples.edit_reflection),
    store: HklCalcStore = Depends(get_store),
):
    await service.edit_reflection(name, params, store)
    return {"message": f"reflection with tag/index {params.tag_or_idx} edited. "}


@router.delete("/{name}/reflection")
async def delete_reflection(
    name: str,
    params: DeleteParams = Body(..., example={"tag_or_idx": "refl1"}),
    store: HklCalcStore = Depends(get_store),
):
    await service.delete_reflection(name, params.tag_or_idx, store)  # TODO Change this!
    return {"message": f"reflection with tag/index {params.tag_or_idx} deleted."}


@router.put("/{name}/orientation")
async def add_orientation(
    name: str,
    params: AddOrientationParams = Body(..., example=examples.add_orientation),
    store: HklCalcStore = Depends(get_store),
):
    await service.add_orientation(name, params, store)
    return {"message": f"added orientation for UB Calculation of crystal {name}"}


@router.patch("/{name}/orientation")
async def edit_orientation(
    name: str,
    params: EditOrientationParams = Body(..., example=examples.edit_orientation),
    store: HklCalcStore = Depends(get_store),
):
    await service.edit_orientation(name, params, store)
    return {"message": f"orientation with tag/index {params.tag_or_idx} edited."}


@router.delete("/{name}/orientation")
async def delete_orientation(
    name: str,
    params: DeleteParams = Body(..., example={"tag_or_idx": "plane"}),
    store: HklCalcStore = Depends(get_store),
):
    await service.delete_orientation(name, params.tag_or_idx, store)
    return {"message": f"reflection with tag or index {params.tag_or_idx} deleted."}


@router.patch("/{name}/lattice")
async def set_lattice(
    name: str,
    params: SetLatticeParams = Body(example=examples.set_lattice),
    store: HklCalcStore = Depends(get_store),
    _=Depends(check_params_not_empty),
):
    await service.set_lattice(name, params, store)
    return {"message": f"lattice has been set for UB calculation of crystal {name}"}


@router.patch("/{name}/{property}")
async def modify_property(
    name: str,
    property: str,
    target_value: Tuple[float, float, float] = Body(..., example=[1, 0, 0]),
    store: HklCalcStore = Depends(get_store),
    _=Depends(check_property_is_valid),
):
    await service.modify_property(name, property, target_value, store)
    return {"message": f"{property} has been set for UB calculation of crystal {name}"}
