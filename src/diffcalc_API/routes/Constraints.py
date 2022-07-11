from typing import Dict, Tuple, Union

from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from fastapi import APIRouter, Body, Depends

from diffcalc_API.config import constraintsWithNoValue
from diffcalc_API.errors.Constraints import check_constraint_exists
from diffcalc_API.fileHandling import pickleHkl, unpickleHkl

router = APIRouter(prefix="/constraints", tags=["constraints"])


singleConstraintType = Union[Tuple[str, float], str]


@router.put("/{name}/set")
async def set_constraints(
    name: str,
    constraintDict: Dict[str, Union[float, bool]] = Body(
        example={"qaz": 0, "alpha": 0, "eta": 0}
    ),
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    booleanConstraints = set(constraintDict.keys()).intersection(constraintsWithNoValue)
    for constraint in booleanConstraints:
        constraintDict[constraint] = bool(constraintDict[constraint])

    hklCalc.constraints = Constraints(constraintDict)
    pickleHkl(hklCalc, name)
    return {"message": f"constraints updated (replaced) for crystal {name}"}


@router.patch("/{name}/unconstrain/{property}")
async def remove_constraint(
    name: str,
    property: str,
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    check_constraint_exists(property)
    setattr(hklCalc.constraints, property, None)
    pickleHkl(hklCalc, name)

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
    hklCalc: HklCalculation = Depends(unpickleHkl),
    value: Union[float, bool] = Body(...),
):
    check_constraint_exists(property)

    if property in constraintsWithNoValue:
        value = bool(value)

    setattr(hklCalc.constraints, property, value)
    pickleHkl(hklCalc, name)

    return {
        "message": (
            f"constrained {property} for crystal {name}. "
            f"Constraints are now: {hklCalc.constraints.asdict}"
        )
    }
