from typing import Dict, Union

from diffcalc.hkl.constraints import Constraints

from diffcalc_API.config import constraintsWithNoValue
from diffcalc_API.errors.Constraints import check_constraint_exists
from diffcalc_API.stores.protocol import HklCalcStore


async def get_constraints(name: str, store: HklCalcStore) -> str:
    hklCalc = await store.load(name)
    return str(hklCalc.constraints)


async def set_constraints(
    name: str,
    constraintDict: Dict[str, Union[float, bool]],
    store: HklCalcStore,
) -> None:
    hklCalc = await store.load(name)

    booleanConstraints = set(constraintDict.keys()).intersection(constraintsWithNoValue)
    for constraint in booleanConstraints:
        constraintDict[constraint] = bool(constraintDict[constraint])

    hklCalc.constraints = Constraints(constraintDict)

    await store.save(name, hklCalc)


async def remove_constraint(
    name: str,
    property: str,
    store: HklCalcStore,
) -> None:
    hklCalc = await store.load(name)

    check_constraint_exists(property)
    setattr(hklCalc.constraints, property, None)

    await store.save(name, hklCalc)


async def set_constraint(
    name: str,
    property: str,
    value: Union[float, bool],
    store: HklCalcStore,
):
    hklCalc = await store.load(name)

    check_constraint_exists(property)
    if property in constraintsWithNoValue:
        value = bool(value)

    setattr(hklCalc.constraints, property, value)

    await store.save(name, hklCalc)
