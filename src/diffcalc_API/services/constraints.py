"""Defines business logic for handling requests from constraints endpoints."""

from typing import Dict, Optional

from diffcalc.hkl.constraints import Constraints

from diffcalc_API.config import ALL_CONSTRAINTS, CONSTRAINTS_WITH_NO_VALUE
from diffcalc_API.errors.constraints import InvalidConstraintError
from diffcalc_API.stores.protocol import HklCalcStore


async def get_constraints(
    name: str, store: HklCalcStore, collection: Optional[str]
) -> str:
    """Get the status of the constraints object in the given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    Returns:
        a string with the current state of the constraints
    """
    hklcalc = await store.load(name, collection)
    return str(hklcalc.constraints)


async def set_constraints(
    name: str,
    constraints: Dict[str, float],
    store: HklCalcStore,
    collection: Optional[str],
) -> None:
    """Set the constraints in the constraints object in the given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        constraints: dictionary with the constraints to set
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    """
    hklcalc = await store.load(name, collection)

    boolean_constraints = set(constraints.keys()).intersection(
        CONSTRAINTS_WITH_NO_VALUE
    )
    for constraint in boolean_constraints:
        constraints[constraint] = bool(constraints[constraint])

    hklcalc.constraints = Constraints(constraints)

    await store.save(name, hklcalc, collection)


async def remove_constraint(
    name: str,
    property: str,
    store: HklCalcStore,
    collection: Optional[str],
) -> None:
    """Remove a constraint in the constraints object in the given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        property: the constraint to remove
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    """
    hklcalc = await store.load(name, collection)

    if property not in ALL_CONSTRAINTS:
        raise InvalidConstraintError(property)

    setattr(hklcalc.constraints, property, None)

    await store.save(name, hklcalc, collection)


async def set_constraint(
    name: str,
    property: str,
    value: float,
    store: HklCalcStore,
    collection: Optional[str],
) -> None:
    """Set a constraint in the constraints object in the given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        property: the constraint to set
        value: the value of the constraint to set to
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    """
    hklcalc = await store.load(name, collection)

    if property not in ALL_CONSTRAINTS:
        raise InvalidConstraintError(property)

    if property in CONSTRAINTS_WITH_NO_VALUE:
        value = bool(value)

    setattr(hklcalc.constraints, property, value)

    await store.save(name, hklcalc, collection)
