"""Business logic for handling requests from ub endpoints."""

from typing import List, Optional, Tuple, Union

import numpy as np
from diffcalc.hkl.geometry import Position
from diffcalc.ub.calc import UBCalculation

from diffcalc_api.errors.ub import NoUbMatrixError, ReferenceRetrievalError
from diffcalc_api.models.ub import (
    AddOrientationParams,
    AddReflectionParams,
    EditOrientationParams,
    EditReflectionParams,
    HklModel,
    PositionModel,
    SetLatticeParams,
    XyzModel,
)
from diffcalc_api.stores.protocol import HklCalcStore


async def get_ub(name: str, store: HklCalcStore, collection: Optional[str]) -> str:
    """Get the status of the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    Returns:
        a string with the current state of the UB object
    """
    hklcalc = await store.load(name, collection)

    return str(hklcalc.ubcalc)


async def add_reflection(
    name: str,
    params: AddReflectionParams,
    store: HklCalcStore,
    collection: Optional[str],
    tag: Optional[str],
) -> None:
    """Add reflection to the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        params: detail about the reflection object to be added
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to attribute to the new reflection

    """
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
    """Modify reflection in the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        params: detail describing what the reflection should be edited to
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to retrieve the reflection by
        idx: optional index to retrieve the reflection by

    Exactly one tag or index must be provided.
    """
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
    """Delete reflection in the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to retrieve the reflection by
        idx: optional index to retrieve the reflection by

    Exactly one tag or index must be provided.
    """
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
    """Add orientation to the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        params: detail about the orientation object to be added
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to attribute to the new orientation

    """
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
    """Modify orientation in the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        params: detail describing what the orientation should be edited to
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to retrieve the orientation by
        idx: optional index to retrieve the orientation by

    Exactly one tag or index must be provided.
    """
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
    """Delete orientation in the UB object in a given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to retrieve the orientation by
        idx: optional index to retrieve the orientation by

    Exactly one tag or index must be provided.
    """
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
    """Set the Crystal parameters in the UB object in a given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        params: the parameters to use to set the lattice
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    """
    hklcalc = await store.load(name, collection)

    input_params = params.dict()
    crystal_name = name if not params.name else params.name
    input_params.pop("name")

    hklcalc.ubcalc.set_lattice(name=crystal_name, **input_params)

    await store.save(name, hklcalc, collection)


async def modify_property(
    name: str,
    property: str,
    target_value: HklModel,
    store: HklCalcStore,
    collection: Optional[str],
) -> None:
    """Set a property of the UB object in a given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        property: the property of the UB object to set
        target_value: the miller indices to set them to
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    The property to be set must be a valid vector property.
    """
    hklcalc = await store.load(name, collection)

    setattr(hklcalc.ubcalc, property, tuple(target_value.dict().values()))

    await store.save(name, hklcalc, collection)


async def set_miscut(
    name: str,
    rot_axis: XyzModel,
    angle: float,
    add_miscut: bool,
    store: HklCalcStore,
    collection: Optional[str],
) -> None:
    """Find the U matrix using a miscut axis/angle, and set this as the new U matrix.

    Args:
        name: the name of the hkl object to access within the store
        rot_axis: the rotational axis of the miscut
        angle: the miscut angle
        add_miscut: if True, apply provided miscu
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    """
    hklcalc = await store.load(name, collection)

    ubcalc: UBCalculation = hklcalc.ubcalc
    ubcalc.set_miscut((rot_axis.x, rot_axis.y, rot_axis.z), angle, add_miscut)

    await store.save(name, hklcalc, collection)


async def get_miscut(
    name: str,
    store: HklCalcStore,
    collection: Optional[str],
) -> Tuple[float, List[float]]:
    hklcalc = await store.load(name, collection)

    ubcalc: UBCalculation = hklcalc.ubcalc
    try:
        angle, axis = ubcalc.get_miscut()
    except ValueError:
        raise NoUbMatrixError()

    return angle, axis.T.tolist()[0]


async def get_miscut_from_hkl(
    name: str,
    hkl: HklModel,
    pos: PositionModel,
    store: HklCalcStore,
    collection: Optional[str],
) -> Tuple[float, Tuple[float, float, float]]:
    hklcalc = await store.load(name, collection)

    ubcalc: UBCalculation = hklcalc.ubcalc
    try:
        angle, axis = ubcalc.get_miscut_from_hkl(
            (hkl.h, hkl.k, hkl.l), Position(**pos.dict())
        )
    except ValueError:
        raise NoUbMatrixError()

    return angle, axis


async def calculate_ub(
    name: str,
    store: HklCalcStore,
    collection: Optional[str],
    tag1: Optional[str],
    idx1: Optional[int],
    tag2: Optional[str],
    idx2: Optional[int],
) -> List[List[float]]:
    """Calculate the UB matrix.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.
        tag1: the tag of the first reference object.
        idx1: the index of the first reference object.
        tag2: the tag of the second reference object.
        idx2: the index of the second reference object.

    For each reference object, only a tag or index needs to be given. If none are
    provided, diffcalc-core tries to work it out from the available reference
    objects.

    Returns:
        a list of angles, combined together into one dictionary.

    """
    hklcalc = await store.load(name, collection)

    first_retrieve: Optional[Union[str, int]] = tag1 if tag1 else idx1
    second_retrieve: Optional[Union[str, int]] = tag2 if tag2 else idx2

    hklcalc.ubcalc.calc_ub(first_retrieve, second_retrieve)

    await store.save(name, hklcalc, collection)
    return np.round(hklcalc.ubcalc.UB, 6).tolist()


async def set_u(
    name: str,
    u_matrix: List[List[float]],
    store: HklCalcStore,
    collection: Optional[str],
):
    hklcalc = await store.load(name, collection)

    ubcalc: UBCalculation = hklcalc.ubcalc
    ubcalc.set_u(u_matrix)

    await store.save(name, hklcalc, collection)


async def set_ub(
    name: str,
    ub_matrix: List[List[float]],
    store: HklCalcStore,
    collection: Optional[str],
):
    hklcalc = await store.load(name, collection)

    ubcalc: UBCalculation = hklcalc.ubcalc
    ubcalc.set_ub(ub_matrix)

    await store.save(name, hklcalc, collection)
