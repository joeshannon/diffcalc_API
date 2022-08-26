"""Endpoints relating to the management of setting up the UB calculation."""

from typing import Optional

from fastapi import APIRouter, Body, Depends, Query

from diffcalc_API.config import VECTOR_PROPERTIES
from diffcalc_API.errors.ub import (
    BothTagAndIdxProvidedError,
    InvalidPropertyError,
    InvalidSetLatticeParamsError,
    NoTagOrIdxProvidedError,
)
from diffcalc_API.examples import ub as examples
from diffcalc_API.models.response import InfoResponse, StringResponse
from diffcalc_API.models.ub import (
    AddOrientationParams,
    AddReflectionParams,
    EditOrientationParams,
    EditReflectionParams,
    HklModel,
    SetLatticeParams,
    select_idx_or_tag_str,
)
from diffcalc_API.services import ub as service
from diffcalc_API.stores.protocol import HklCalcStore, get_store

router = APIRouter(prefix="/ub", tags=["ub"])


@router.get("/{name}", response_model=StringResponse)
async def get_ub(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Get the status of the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    Returns:
        a string with the current state of the UB object
    """
    content = await service.get_ub(name, store, collection)
    return StringResponse(payload=content)


@router.post("/{name}/reflection", response_model=InfoResponse)
async def add_reflection(
    name: str,
    params: AddReflectionParams = Body(..., example=examples.add_reflection),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
    tag: Optional[str] = Query(default=None, example="refl1"),
):
    """Add reflection to the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        params: detail about the reflection object to be added
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to attribute to the new reflection

    """
    await service.add_reflection(name, params, store, collection, tag)
    return InfoResponse(
        message=(
            f"added reflection for UB Calculation of crystal {name} in "
            + f"collection {collection}"
        )
    )


@router.put("/{name}/reflection", response_model=InfoResponse)
async def edit_reflection(
    name: str,
    params: EditReflectionParams = Body(..., example=examples.edit_reflection),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
    tag: Optional[str] = Query(default=None, example="refl1"),
    idx: Optional[int] = Query(default=None),
):
    """Modify reflection in the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        params: detail describing what the reflection should be edited to
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to retrieve the reflection by
        idx: optional index to retrieve the reflection by

    Exactly one tag or index must be provided.
    """
    if (tag is None) and (idx is None):
        raise NoTagOrIdxProvidedError()

    if (tag is not None) and (idx is not None):
        raise BothTagAndIdxProvidedError()

    await service.edit_reflection(name, params, store, collection, tag, idx)
    return InfoResponse(
        message=(
            f"reflection of crystal {name} in collection {collection} with "
            + f"{select_idx_or_tag_str(idx, tag)} edited"
        )
    )


@router.delete("/{name}/reflection", response_model=InfoResponse)
async def delete_reflection(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
    tag: Optional[str] = Query(default=None, example="refl1"),
    idx: Optional[int] = Query(default=None),
):
    """Delete reflection in the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to retrieve the reflection by
        idx: optional index to retrieve the reflection by

    Exactly one tag or index must be provided.
    """
    if (idx is None) and (tag is None):
        raise NoTagOrIdxProvidedError()
    if (idx is not None) and (tag is not None):
        raise BothTagAndIdxProvidedError()

    await service.delete_reflection(name, store, collection, tag, idx)
    return InfoResponse(
        message=(
            f"reflection of crystal {name} in collection {collection} "
            + f"with {select_idx_or_tag_str(idx, tag)} deleted"
        )
    )


@router.post("/{name}/orientation", response_model=InfoResponse)
async def add_orientation(
    name: str,
    params: AddOrientationParams = Body(..., example=examples.add_orientation),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
    tag: Optional[str] = Query(default=None, example="plane"),
):
    """Add orientation to the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        params: detail about the orientation object to be added
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to attribute to the new orientation

    """
    await service.add_orientation(name, params, store, collection, tag)
    return InfoResponse(
        message=(
            f"added orientation for UB Calculation of crystal {name} in "
            + f"collection {collection}"
        )
    )


@router.put("/{name}/orientation", response_model=InfoResponse)
async def edit_orientation(
    name: str,
    params: EditOrientationParams = Body(..., example=examples.edit_orientation),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
    tag: Optional[str] = Query(default=None),
    idx: Optional[int] = Query(default=None, example=0),
):
    """Modify orientation in the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        params: detail describing what the orientation should be edited to
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to retrieve the orientation by
        idx: optional index to retrieve the orientation by

    Exactly one tag or index must be provided.
    """
    if (idx is None) and (tag is None):
        raise NoTagOrIdxProvidedError()
    if (idx is not None) and (tag is not None):
        raise BothTagAndIdxProvidedError()

    await service.edit_orientation(name, params, store, collection, tag, idx)
    return InfoResponse(
        message=(
            f"orientation of crystal {name} in collection {collection} with "
            f"{select_idx_or_tag_str(idx, tag)} edited"
        )
    )


@router.delete("/{name}/orientation", response_model=InfoResponse)
async def delete_orientation(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
    tag: Optional[str] = Query(default=None, example="plane"),
    idx: Optional[int] = Query(default=None),
):
    """Delete orientation in the UB object in a given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to retrieve the orientation by
        idx: optional index to retrieve the orientation by

    Exactly one tag or index must be provided.
    """
    if (idx is None) and (tag is None):
        raise NoTagOrIdxProvidedError()
    if (idx is not None) and (tag is not None):
        raise BothTagAndIdxProvidedError()

    await service.delete_orientation(name, store, collection, tag, idx)
    return InfoResponse(
        message=(
            f"orientation of crystal {name} in collection {collection} "
            + f"with {select_idx_or_tag_str(idx, tag)} deleted"
        )
    )


@router.patch("/{name}/lattice", response_model=InfoResponse)
async def set_lattice(
    name: str,
    params: SetLatticeParams = Body(example=examples.set_lattice),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Set the Crystal parameters in the UB object in a given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        params: the parameters to use to set the lattice
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    """
    non_empty_vars = [var for var, value in params if value is not None]

    if len(non_empty_vars) == 0:
        raise InvalidSetLatticeParamsError()

    await service.set_lattice(name, params, store, collection)
    return InfoResponse(
        message=(
            f"lattice has been set for UB calculation of crystal {name} in "
            + f"collection {collection}"
        )
    )


@router.put("/{name}/{property}", response_model=InfoResponse)
async def modify_property(
    name: str,
    property: str,
    target_value: HklModel = Body(..., example={"h": 1, "k": 0, "l": 0}),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Set a property of the UB object in a given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        property: the property of the UB object to set
        target_value: the miller indices to set them to
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    The property to be set must be a valid vector property.
    """
    if property not in VECTOR_PROPERTIES:
        raise InvalidPropertyError()

    await service.modify_property(name, property, target_value, store, collection)
    return InfoResponse(
        message=(
            f"{property} has been set for UB calculation of crystal {name} in "
            + f"collection {collection}"
        )
    )
