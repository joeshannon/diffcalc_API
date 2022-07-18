from typing import Dict, Union

from diffcalc.hkl.constraints import Constraints

from diffcalc_API.config import constraints_with_no_value
from diffcalc_API.errors.constraints import check_constraint_exists
from diffcalc_API.stores.protocol import HklCalcStore


async def get_constraints(name: str, store: HklCalcStore) -> str:
    hklcalc = await store.load(name)
    return str(hklcalc.constraints)


async def set_constraints(
    name: str,
    constraints: Dict[str, Union[float, bool]],
    store: HklCalcStore,
) -> None:
    hklcalc = await store.load(name)

    boolean_constraints = set(constraints.keys()).intersection(
        constraints_with_no_value
    )
    for constraint in boolean_constraints:
        constraints[constraint] = bool(constraints[constraint])

    hklcalc.constraints = Constraints(constraints)

    await store.save(name, hklcalc)


async def remove_constraint(
    name: str,
    property: str,
    store: HklCalcStore,
) -> None:
    hklcalc = await store.load(name)

    check_constraint_exists(property)
    setattr(hklcalc.constraints, property, None)

    await store.save(name, hklcalc)


async def set_constraint(
    name: str,
    property: str,
    value: Union[float, bool],
    store: HklCalcStore,
):
    hklcalc = await store.load(name)

    check_constraint_exists(property)
    if property in constraints_with_no_value:
        value = bool(value)

    setattr(hklcalc.constraints, property, value)

    await store.save(name, hklcalc)
