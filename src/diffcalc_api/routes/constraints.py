"""Endpoints relating to the management of constraints."""

from typing import Dict, Optional

from fastapi import APIRouter, Body, Depends, Query

from diffcalc_api.models.response import InfoResponse, StringResponse
from diffcalc_api.services import constraints as service
from diffcalc_api.stores.protocol import HklCalcStore, get_store

router = APIRouter(prefix="/constraints", tags=["constraints"])


@router.get("/{name}", response_model=StringResponse)
async def get_constraints(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Get the status of the constraints object in the given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    Returns:
        StringResponse with the state of the contsraints object.
    """
    content = await service.get_constraints(name, store, collection)
    return StringResponse(payload=content)


@router.post("/{name}", response_model=InfoResponse)
async def set_constraints(
    name: str,
    constraints: Dict[str, float] = Body(example={"qaz": 0, "alpha": 0, "eta": 0}),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Set the constraints in the constraints object in the given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        constraints: dictionary with the constraints to set
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    """
    await service.set_constraints(name, constraints, store, collection)
    return InfoResponse(
        message=(
            f"constraints updated (replaced) for crystal {name} in "
            + f"collection {collection}"
        )
    )


@router.delete("/{name}/{property}", response_model=InfoResponse)
async def remove_constraint(
    name: str,
    property: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Remove a constraint in the constraints object in the given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        property: the constraint to remove
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    """
    await service.remove_constraint(name, property, store, collection)

    return InfoResponse(
        message=(
            f"unconstrained {property} for crystal {name} in "
            + f"collection {collection}. "
        )
    )


@router.patch("/{name}/{property}", response_model=InfoResponse)
async def set_constraint(
    name: str,
    property: str,
    value: float = Body(...),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Set a constraint in the constraints object in the given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        property: the constraint to set
        value: the value of the constraint to set to
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    """
    await service.set_constraint(name, property, value, store, collection)

    return InfoResponse(
        message=(
            f"constrained {property} for crystal {name} in collection "
            + f"{collection}. "
        )
    )
