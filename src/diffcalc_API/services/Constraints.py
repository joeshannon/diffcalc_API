from typing import Dict, Union

from diffcalc.hkl.constraints import Constraints

from diffcalc_API.config import constraintsWithNoValue
from diffcalc_API.errors.Constraints import check_constraint_exists
from diffcalc_API.persistence import HklCalcRepo


async def get_constraints(name: str, repo: HklCalcRepo) -> str:
    hklCalc = await repo.load(name)
    return str(hklCalc.constraints)


async def set_constraints(
    name: str,
    constraintDict: Dict[str, Union[float, bool]],
    repo: HklCalcRepo,
) -> None:
    hklCalc = await repo.load(name)

    booleanConstraints = set(constraintDict.keys()).intersection(constraintsWithNoValue)
    for constraint in booleanConstraints:
        constraintDict[constraint] = bool(constraintDict[constraint])

    hklCalc.constraints = Constraints(constraintDict)

    await repo.save(name, hklCalc)


async def remove_constraint(
    name: str,
    property: str,
    repo: HklCalcRepo,
) -> None:
    hklCalc = await repo.load(name)

    check_constraint_exists(property)
    setattr(hklCalc.constraints, property, None)

    await repo.save(name, hklCalc)


async def set_constraint(
    name: str,
    property: str,
    value: Union[float, bool],
    repo: HklCalcRepo,
):
    hklCalc = await repo.load(name)

    check_constraint_exists(property)
    if property in constraintsWithNoValue:
        value = bool(value)

    setattr(hklCalc.constraints, property, value)

    await repo.save(name, hklCalc)
