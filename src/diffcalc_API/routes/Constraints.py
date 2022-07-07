from typing import Dict, Tuple, Union

from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from fastapi import APIRouter, Body, Depends, HTTPException

from diffcalc_API.utils import (
    allConstraints,
    constraintsWithNoValue,
    pickleHkl,
    unpickleHkl,
)

router = APIRouter(prefix="/update/constraints", tags=["constraints"])


singleConstraintType = Union[Tuple[str, float], str]


@router.post("/{name}/set")
async def set_constraints(
    name: str,
    constraintDict: Dict[str, Union[float, bool]] = Body(
        example={"qaz": 0, "alpha": 0, "eta": 0}
    ),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    booleanConstraints = set(constraintDict.keys()).intersection(constraintsWithNoValue)
    for constraint in booleanConstraints:
        constraintDict[constraint] = bool(constraintDict[constraint])

    constraints = Constraints(constraintDict)

    hkl.constraints = constraints
    pickleHkl(hkl, name)
    return {"message": f"constraints updated (replaced) for crystal {name}"}


@router.post("/{name}/unconstrain/{property}")
async def remove_constraint(
    name: str,
    property: str,
    hkl: HklCalculation = Depends(unpickleHkl),
):
    check_constraint_exists(property)
    setattr(hkl.constraints, property, None)
    pickleHkl(hkl, name)

    return {
        "message": (
            f"unconstrained {property} for crystal {name}. "
            f"Constraints are now: {hkl.constraints.asdict}"
        )
    }


@router.post("/{name}/constrain/{property}")
async def set_constraint(
    name: str,
    property: str,
    hkl: HklCalculation = Depends(unpickleHkl),
    value: Union[float, bool] = Body(...),
):
    check_constraint_exists(property)

    if property in constraintsWithNoValue:
        value = bool(value)

    try:
        setattr(hkl.constraints, property, value)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"{e}")

    pickleHkl(hkl, name)
    return {
        "message": (
            f"constrained {property} for crystal {name}. "
            f"Constraints are now: {hkl.constraints.asdict}"
        )
    }


def check_constraint_exists(constraint: str):
    if constraint not in allConstraints:
        raise HTTPException(
            status_code=402,
            detail=(
                f"property {constraint} does not exist as a valid constraint."
                f" Choose one of {allConstraints}"
            ),
        )
