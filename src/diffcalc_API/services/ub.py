from typing import Optional, Union

from diffcalc.hkl.geometry import Position

from diffcalc_API.errors.ub import ReferenceRetrievalError
from diffcalc_API.models.ub import (
    AddOrientationParams,
    AddReflectionParams,
    EditOrientationParams,
    EditReflectionParams,
    HklModel,
    SetLatticeParams,
)
from diffcalc_API.stores.protocol import HklCalcStore


async def get_ub(name: str, store: HklCalcStore, collection: Optional[str]) -> str:
    hklcalc = await store.load(name, collection)

    return str(hklcalc.ubcalc)


async def add_reflection(
    name: str,
    params: AddReflectionParams,
    store: HklCalcStore,
    collection: Optional[str],
) -> None:
    hklcalc = await store.load(name, collection)

    hklcalc.ubcalc.add_reflection(
        tuple(params.hkl.dict().values()),
        Position(**params.position.dict()),
        params.energy,
        params.tag,
    )

    await store.save(name, hklcalc, collection)


async def edit_reflection(
    name: str,
    params: EditReflectionParams,
    store: HklCalcStore,
    collection: Optional[str],
) -> None:
    hklcalc = await store.load(name, collection)

    retrieve: Optional[Union[int, str]] = (
        params.retrieve_idx if params.retrieve_idx is not None else params.retrieve_tag
    )

    try:
        reflection = hklcalc.ubcalc.get_reflection(retrieve)
    except (IndexError, ValueError):
        raise ReferenceRetrievalError(retrieve, "reflection")

    inputs = {
        "idx": retrieve,
        "hkl": (reflection.h, reflection.k, reflection.l),
        "position": reflection.pos,
        "energy": reflection.energy,
        "tag": params.set_tag,
    }

    if params.hkl:
        inputs["hkl"] = tuple(params.hkl.dict().values())
    if params.position:
        inputs["position"] = Position(**params.position.dict())
    if params.energy:
        inputs["energy"] = params.energy

    hklcalc.ubcalc.edit_reflection(**inputs)

    await store.save(name, hklcalc, collection)


async def delete_reflection(
    name: str,
    tag_or_idx: Union[str, int],
    store: HklCalcStore,
    collection: Optional[str],
) -> None:
    hklcalc = await store.load(name, collection)

    try:
        hklcalc.ubcalc.get_reflection(tag_or_idx)
    except (IndexError, ValueError):
        raise ReferenceRetrievalError(tag_or_idx, "reflection")

    hklcalc.ubcalc.del_reflection(tag_or_idx)

    await store.save(name, hklcalc, collection)


async def add_orientation(
    name: str,
    params: AddOrientationParams,
    store: HklCalcStore,
    collection: Optional[str],
) -> None:
    hklcalc = await store.load(name, collection)

    position = Position(*params.position.dict()) if params.position else None
    hklcalc.ubcalc.add_orientation(
        tuple(params.hkl.dict().values()),
        tuple(params.xyz.dict().values()),
        position,
        params.tag,
    )

    await store.save(name, hklcalc, collection)


async def edit_orientation(
    name: str,
    params: EditOrientationParams,
    store: HklCalcStore,
    collection: Optional[str],
) -> None:
    hklcalc = await store.load(name, collection)

    retrieve: Optional[Union[int, str]] = (
        params.retrieve_idx if params.retrieve_idx is not None else params.retrieve_tag
    )
    try:
        orientation = hklcalc.ubcalc.get_orientation(retrieve)
    except (IndexError, ValueError):
        raise ReferenceRetrievalError(retrieve, "reflection")

    inputs = {
        "idx": retrieve,
        "hkl": (orientation.h, orientation.k, orientation.l),
        "xyz": (orientation.x, orientation.y, orientation.z),
        "position": orientation.pos,
        "tag": params.set_tag,
    }

    if params.hkl:
        inputs["hkl"] = tuple(params.hkl.dict().values())
    if params.xyz:
        inputs["xyz"] = tuple(params.xyz.dict().values())
    if params.position:
        inputs["position"] = Position(**params.position.dict())

    hklcalc.ubcalc.edit_orientation(**inputs)

    await store.save(name, hklcalc, collection)


async def delete_orientation(
    name: str,
    tag_or_idx: Union[str, int],
    store: HklCalcStore,
    collection: Optional[str],
) -> None:
    hklcalc = await store.load(name, collection)

    try:
        hklcalc.ubcalc.get_orientation(tag_or_idx)
    except (IndexError, ValueError):
        raise ReferenceRetrievalError(tag_or_idx, "orientation")

    hklcalc.ubcalc.del_orientation(tag_or_idx)

    await store.save(name, hklcalc, collection)


async def set_lattice(
    name: str, params: SetLatticeParams, store: HklCalcStore, collection: Optional[str]
) -> None:
    hklcalc = await store.load(name, collection)

    hklcalc.ubcalc.set_lattice(name=name, **params.dict())

    await store.save(name, hklcalc, collection)


async def modify_property(
    name: str,
    property: str,
    target_value: HklModel,
    store: HklCalcStore,
    collection: Optional[str],
) -> None:
    hklcalc = await store.load(name, collection)

    setattr(hklcalc.ubcalc, property, tuple(target_value.dict().values()))

    await store.save(name, hklcalc, collection)
