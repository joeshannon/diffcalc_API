from typing import Dict, Optional

from fastapi import APIRouter, Body, Depends, Query

from diffcalc_API.models.response import InfoResponse, StringResponse
from diffcalc_API.services import constraints as service
from diffcalc_API.stores.protocol import HklCalcStore, get_store

router = APIRouter(prefix="/constraints", tags=["constraints"])


@router.get("/{name}", response_model=StringResponse)
async def get_constraints(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    content = await service.get_constraints(name, store, collection)
    return StringResponse(payload=content)


@router.post("/{name}", response_model=InfoResponse)
async def set_constraints(
    name: str,
    constraints: Dict[str, float] = Body(example={"qaz": 0, "alpha": 0, "eta": 0}),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
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
    await service.set_constraint(name, property, value, store, collection)

    return InfoResponse(
        message=(
            f"constrained {property} for crystal {name} in collection "
            + f"{collection}. "
        )
    )
