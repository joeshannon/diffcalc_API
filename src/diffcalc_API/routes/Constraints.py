from pathlib import Path
from typing import Callable, Dict, Union

from diffcalc.hkl.calc import HklCalculation
from fastapi import APIRouter, Body, Depends

from diffcalc_API.fileHandling import supplyPersist, unpickleHkl
from diffcalc_API.services import Constraints as service

router = APIRouter(prefix="/constraints", tags=["constraints"])


@router.put("/{name}/set")
async def set_constraints(
    name: str,
    constraintDict: Dict[str, Union[float, bool]] = Body(
        example={"qaz": 0, "alpha": 0, "eta": 0}
    ),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    service.set_constraints(name, constraintDict, hklCalc, persist)
    return {"message": f"constraints updated (replaced) for crystal {name}"}


@router.patch("/{name}/unconstrain/{property}")
async def remove_constraint(
    name: str,
    property: str,
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    service.remove_constraint(name, property, hklCalc, persist)

    return {
        "message": (
            f"unconstrained {property} for crystal {name}. "
            f"Constraints are now: {hklCalc.constraints.asdict}"
        )
    }


@router.patch("/{name}/constrain/{property}")
async def set_constraint(
    name: str,
    property: str,
    value: Union[float, bool] = Body(...),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    service.set_constraint(name, property, value, hklCalc, persist)

    return {
        "message": (
            f"constrained {property} for crystal {name}. "
            f"Constraints are now: {hklCalc.constraints.asdict}"
        )
    }
