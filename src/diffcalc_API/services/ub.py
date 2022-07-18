from typing import Tuple, Union

from diffcalc.hkl.geometry import Position

from diffcalc_API.errors.ub import get_orientation, get_reflection
from diffcalc_API.models.ub import (
    AddOrientationParams,
    AddReflectionParams,
    EditOrientationParams,
    EditReflectionParams,
    SetLatticeParams,
)
from diffcalc_API.stores.protocol import HklCalcStore


async def get_ub(name: str, store: HklCalcStore) -> str:
    hklcalc = await store.load(name)

    return str(hklcalc.ubcalc)


async def add_reflection(
    name: str,
    params: AddReflectionParams,
    store: HklCalcStore,
) -> None:
    hklcalc = await store.load(name)

    hklcalc.ubcalc.add_reflection(
        params.hkl,
        Position(*params.position),
        params.energy,
        params.tag,
    )

    await store.save(name, hklcalc)


async def edit_reflection(
    name: str,
    params: EditReflectionParams,
    store: HklCalcStore,
) -> None:
    hklcalc = await store.load(name)

    reflection = get_reflection(hklcalc, params.tag_or_idx)
    hklcalc.ubcalc.edit_reflection(
        params.tag_or_idx,
        params.hkl if params.hkl else (reflection.h, reflection.k, reflection.l),
        Position(params.position) if params.position else reflection.pos,
        params.energy if params.energy else reflection.energy,
        params.tag_or_idx if isinstance(params.tag_or_idx, str) else None,
    )

    await store.save(name, hklcalc)


async def delete_reflection(
    name: str,
    tag_or_idx: Union[str, int],
    store: HklCalcStore,
) -> None:
    hklcalc = await store.load(name)

    _ = get_reflection(hklcalc, tag_or_idx)
    hklcalc.ubcalc.del_reflection(tag_or_idx)

    await store.save(name, hklcalc)


async def add_orientation(
    name: str,
    params: AddOrientationParams,
    store: HklCalcStore,
) -> None:
    hklcalc = await store.load(name)

    position = Position(*params.position) if params.position else None
    hklcalc.ubcalc.add_orientation(
        params.hkl,
        params.xyz,
        position,
        params.tag,
    )

    await store.save(name, hklcalc)


async def edit_orientation(
    name: str,
    params: EditOrientationParams,
    store: HklCalcStore,
) -> None:
    hklcalc = await store.load(name)

    orientation = get_orientation(hklcalc, params.tag_or_idx)
    hklcalc.ubcalc.edit_orientation(
        params.tag_or_idx,
        params.hkl if params.hkl else (orientation.h, orientation.k, orientation.l),
        params.xyz if params.xyz else (orientation.x, orientation.y, orientation.z),
        Position(params.position) if params.position else orientation.pos,
        params.tag_or_idx if isinstance(params.tag_or_idx, str) else None,
    )

    await store.save(name, hklcalc)


async def delete_orientation(
    name: str,
    tag_or_idx: Union[str, int],
    store: HklCalcStore,
) -> None:
    hklcalc = await store.load(name)

    _ = get_orientation(hklcalc, tag_or_idx)
    hklcalc.ubcalc.del_orientation(tag_or_idx)

    await store.save(name, hklcalc)


async def set_lattice(name: str, params: SetLatticeParams, store: HklCalcStore) -> None:
    hklcalc = await store.load(name)

    hklcalc.ubcalc.set_lattice(name=name, **params.dict())

    await store.save(name, hklcalc)


async def modify_property(
    name: str,
    property: str,
    target_value: Tuple[float, float, float],
    store: HklCalcStore,
) -> None:
    hklcalc = await store.load(name)

    setattr(hklcalc.ubcalc, property, target_value)

    await store.save(name, hklcalc)
