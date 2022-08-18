from typing import Optional

from fastapi import APIRouter, Body, Depends, Query

from diffcalc_API.config import VECTOR_PROPERTIES
from diffcalc_API.errors.ub import (
    InvalidPropertyError,
    InvalidSetLatticeParamsError,
    NoTagOrIdxProvidedError,
)
from diffcalc_API.examples import ub as examples
from diffcalc_API.models.ub import (
    AddOrientationParams,
    AddReflectionParams,
    EditOrientationParams,
    EditReflectionParams,
    HklModel,
    SetLatticeParams,
)
from diffcalc_API.services import ub as service
from diffcalc_API.stores.protocol import HklCalcStore, get_store

router = APIRouter(prefix="/ub", tags=["ub"])


@router.get("/{name}")
async def get_ub(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    content = await service.get_ub(name, store, collection)
    return {"payload": content}


@router.post("/{name}/reflection")
async def add_reflection(
    name: str,
    params: AddReflectionParams = Body(..., example=examples.add_reflection),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    await service.add_reflection(name, params, store, collection)
    return {
        "message": (
            f"added reflection for UB Calculation of crystal {name} in "
            + f"collection {collection}"
        )
    }


@router.put("/{name}/reflection")
async def edit_reflection(
    name: str,
    params: EditReflectionParams = Body(..., example=examples.edit_reflection),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    if (params.retrieve_idx is None) and (params.retrieve_tag is None):
        raise NoTagOrIdxProvidedError()

    refl: str = (
        f"index {params.retrieve_idx}"
        if params.retrieve_idx is not None
        else f"tag {params.retrieve_tag}"
    )
    await service.edit_reflection(name, params, store, collection)
    return {
        "message": (
            f"reflection of crystal {name} in collection {collection} "
            + "with %s edited" % refl
        )
    }


@router.delete("/{name}/reflection")
async def delete_reflection(
    name: str,
    tag: str = Query(default=None, example="refl1"),
    idx: int = Query(default=None),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    if (idx is None) and (tag is None):
        raise NoTagOrIdxProvidedError()

    refl: str = f"index {idx}" if idx is not None else f"tag {tag}"

    await service.delete_reflection(
        name, idx if idx is not None else tag, store, collection
    )
    return {
        "message": (
            f"reflection of crystal {name} in collection {collection} "
            + "with %s deleted" % refl
        )
    }


@router.post("/{name}/orientation")
async def add_orientation(
    name: str,
    params: AddOrientationParams = Body(..., example=examples.add_orientation),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    await service.add_orientation(name, params, store, collection)
    return {
        "message": (
            f"added orientation for UB Calculation of crystal {name} in "
            + f"collection {collection}"
        )
    }


@router.put("/{name}/orientation")
async def edit_orientation(
    name: str,
    params: EditOrientationParams = Body(..., example=examples.edit_orientation),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    if (params.retrieve_idx is None) and (params.retrieve_tag is None):
        raise NoTagOrIdxProvidedError()

    orient: str = (
        f"index {params.retrieve_idx}"
        if params.retrieve_idx is not None
        else f"tag {params.retrieve_tag}"
    )
    await service.edit_orientation(name, params, store, collection)
    return {
        "message": (
            f"orientation of crystal {name} in collection {collection} "
            + "with %s edited" % orient
        )
    }


@router.delete("/{name}/orientation")
async def delete_orientation(
    name: str,
    tag: str = Query(default=None, example="plane"),
    idx: int = Query(default=None),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    if (idx is None) and (tag is None):
        raise NoTagOrIdxProvidedError()

    orient: str = f"index {idx}" if idx is not None else f"tag {tag}"

    await service.delete_orientation(
        name, idx if idx is not None else tag, store, collection
    )
    return {
        "message": (
            f"orientation of crystal {name} in collection {collection} "
            + "with %s deleted" % orient
        )
    }


@router.patch("/{name}/lattice")
async def set_lattice(
    name: str,
    params: SetLatticeParams = Body(example=examples.set_lattice),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    non_empty_vars = [var for var, value in params if value is not None]

    if len(non_empty_vars) == 0:
        raise InvalidSetLatticeParamsError()

    await service.set_lattice(name, params, store, collection)
    return {
        "message": (
            f"lattice has been set for UB calculation of crystal {name} in "
            + f"collection {collection}"
        )
    }


@router.put("/{name}/{property}")
async def modify_property(
    name: str,
    property: str,
    target_value: HklModel = Body(..., example={"h": 1, "k": 0, "l": 0}),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    if property not in VECTOR_PROPERTIES:
        raise InvalidPropertyError()

    await service.modify_property(name, property, target_value, store, collection)
    return {
        "message": (
            f"{property} has been set for UB calculation of crystal {name} in "
            + f"collection {collection}"
        )
    }
