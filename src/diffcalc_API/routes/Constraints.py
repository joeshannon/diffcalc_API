from pathlib import Path
from typing import Callable, Dict, Tuple, Union

from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from fastapi import APIRouter, Body, Depends, Response

from diffcalc_API.config import constraintsWithNoValue
from diffcalc_API.errors.Constraints import check_constraint_exists
from diffcalc_API.fileHandling import supplyPersist, unpickleHkl

router = APIRouter(prefix="/constraints", tags=["constraints"])


singleConstraintType = Union[Tuple[str, float], str]


@router.get("/{name}")
async def get_constraints_status(
    name: str, hklCalc: HklCalculation = Depends(unpickleHkl)
):
    return Response(content=str(hklCalc.constraints), media_type="application/text")


@router.put("/{name}/set")
async def set_constraints(
    name: str,
    constraintDict: Dict[str, Union[float, bool]] = Body(
        example={"qaz": 0, "alpha": 0, "eta": 0}
    ),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    booleanConstraints = set(constraintDict.keys()).intersection(constraintsWithNoValue)
    for constraint in booleanConstraints:
        constraintDict[constraint] = bool(constraintDict[constraint])

    hklCalc.constraints = Constraints(constraintDict)
    persist(hklCalc, name)
    return {"message": f"constraints updated (replaced) for crystal {name}"}


@router.patch("/{name}/unconstrain/{property}")
async def remove_constraint(
    name: str,
    property: str,
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    check_constraint_exists(property)
    setattr(hklCalc.constraints, property, None)
    persist(hklCalc, name)

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
    check_constraint_exists(property)

    if property in constraintsWithNoValue:
        value = bool(value)

    setattr(hklCalc.constraints, property, value)
    persist(hklCalc, name)

    return {
        "message": (
            f"constrained {property} for crystal {name}. "
            f"Constraints are now: {hklCalc.constraints.asdict}"
        )
    }
