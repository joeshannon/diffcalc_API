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
    tag: Optional[str],
) -> None:
    hklcalc = await store.load(name, collection)

    hklcalc.ubcalc.add_reflection(
        tuple(params.hkl.dict().values()),
        Position(**params.position.dict()),
        params.energy,
        tag,
    )

    await store.save(name, hklcalc, collection)


async def edit_reflection(
    name: str,
    params: EditReflectionParams,
    store: HklCalcStore,
    collection: Optional[str],
    tag: Optional[str],
    idx: Optional[int],
) -> None:
    hklcalc = await store.load(name, collection)

    retrieve: Union[int, str] = (
        tag if tag is not None else (idx if idx is not None else 0)
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
        "tag": params.set_tag if params.set_tag else reflection.tag,
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
    store: HklCalcStore,
    collection: Optional[str],
    tag: Optional[str],
    idx: Optional[int],
) -> None:
    hklcalc = await store.load(name, collection)

    retrieve: Union[str, int] = (
        tag if tag is not None else (idx if idx is not None else 0)
    )

    try:
        hklcalc.ubcalc.get_reflection(retrieve)
    except (IndexError, ValueError):
        raise ReferenceRetrievalError(retrieve, "reflection")

    hklcalc.ubcalc.del_reflection(retrieve)

    await store.save(name, hklcalc, collection)


async def add_orientation(
    name: str,
    params: AddOrientationParams,
    store: HklCalcStore,
    collection: Optional[str],
    tag: Optional[str],
) -> None:
    hklcalc = await store.load(name, collection)

    position = Position(**params.position.dict()) if params.position else None
    hklcalc.ubcalc.add_orientation(
        tuple(params.hkl.dict().values()),
        tuple(params.xyz.dict().values()),
        position,
        tag,
    )

    await store.save(name, hklcalc, collection)


async def edit_orientation(
    name: str,
    params: EditOrientationParams,
    store: HklCalcStore,
    collection: Optional[str],
    tag: Optional[str],
    idx: Optional[int],
) -> None:
    hklcalc = await store.load(name, collection)

    retrieve: Union[int, str] = (
        tag if tag is not None else (idx if idx is not None else 0)
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
        "tag": params.set_tag if params.set_tag else orientation.tag,
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
    store: HklCalcStore,
    collection: Optional[str],
    tag: Optional[str],
    idx: Optional[int],
) -> None:
    hklcalc = await store.load(name, collection)

    retrieve: Union[int, str] = (
        tag if tag is not None else (idx if idx is not None else 0)
    )

    try:
        hklcalc.ubcalc.get_orientation(retrieve)
    except (IndexError, ValueError):
        raise ReferenceRetrievalError(retrieve, "orientation")

    hklcalc.ubcalc.del_orientation(retrieve)

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
