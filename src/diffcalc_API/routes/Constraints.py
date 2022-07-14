from typing import Dict, Union

from fastapi import APIRouter, Body, Depends, Response

from diffcalc_API.persistence import HklCalcRepo, get_repo
from diffcalc_API.services import Constraints as service

router = APIRouter(prefix="/constraints", tags=["constraints"])


@router.get("/{name}")
async def get_constraints(name: str, repo: HklCalcRepo = Depends(get_repo)):
    content = await service.get_constraints(name, repo)

    return Response(content=content, media_type="application/text")


@router.put("/{name}/set")
async def set_constraints(
    name: str,
    constraintDict: Dict[str, Union[float, bool]] = Body(
        example={"qaz": 0, "alpha": 0, "eta": 0}
    ),
    repo: HklCalcRepo = Depends(get_repo),
):
    await service.set_constraints(name, constraintDict, repo)

    return {"message": f"constraints updated (replaced) for crystal {name}"}


@router.patch("/{name}/unconstrain/{property}")
async def remove_constraint(
    name: str,
    property: str,
    repo: HklCalcRepo = Depends(get_repo),
):
    await service.remove_constraint(name, property, repo)

    return {"message": f"unconstrained {property} for crystal {name}. "}


@router.patch("/{name}/constrain/{property}")
async def set_constraint(
    name: str,
    property: str,
    value: Union[float, bool] = Body(...),
    repo: HklCalcRepo = Depends(get_repo),
):
    await service.set_constraint(name, property, value, repo)

    return {"message": f"constrained {property} for crystal {name}. "}
