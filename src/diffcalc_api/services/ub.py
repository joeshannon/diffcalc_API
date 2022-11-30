"""Business logic for handling requests from ub endpoints."""

from typing import List, Literal, Optional, Tuple, Union, cast

import numpy as np
from diffcalc.hkl.geometry import Position
from diffcalc.ub.calc import UBCalculation
from diffcalc.ub.reference import Orientation, Reflection

from diffcalc_api.errors.ub import (
    InvalidIndexError,
    NoCrystalError,
    NoUbMatrixError,
    ReferenceRetrievalError,
)
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


async def get_ub_status(
    name: str, store: HklCalcStore, collection: Optional[str]
) -> str:
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


#######################################################################################
#                                     Reflections                                     #
#######################################################################################


async def get_reflection(
    name: str,
    store: HklCalcStore,
    collection: Optional[str],
    tag: Optional[str],
    idx: Optional[int],
) -> Reflection:
    hklcalc = await store.load(name, collection)
    ubcalc: UBCalculation = hklcalc.ubcalc

    retrieve: Union[int, str] = (
        tag if tag is not None else (idx if idx is not None else 0)
    )

    try:
        reflection = ubcalc.get_reflection(retrieve)
    except (IndexError, ValueError):
        raise ReferenceRetrievalError(retrieve, "reflection")

    return reflection


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


#######################################################################################
#                                    Orientations                                     #
#######################################################################################


async def get_orientation(
    name: str,
    store: HklCalcStore,
    collection: Optional[str],
    tag: Optional[str],
    idx: Optional[int],
) -> Orientation:
    hklcalc = await store.load(name, collection)
    ubcalc: UBCalculation = hklcalc.ubcalc

    retrieve: Union[int, str] = (
        tag if tag is not None else (idx if idx is not None else 0)
    )

    try:
        orientation = ubcalc.get_orientation(retrieve)
    except (IndexError, ValueError):
        raise ReferenceRetrievalError(retrieve, "orientation")

    return orientation


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
        raise ReferenceRetrievalError(retrieve, "orientation")

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


#######################################################################################
#                                       Crystal                                       #
#######################################################################################


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


#######################################################################################
#                                       Miscuts                                       #
#######################################################################################


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
        add_miscut: boolean determining extra processing on U matrix before it is set
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
    """Get the rotation axis and angle of the miscut, using current UB matrix.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    Returns:
        miscut angle and miscut axis as a list.
    """
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
    """Get the rotation axis and angle of the miscut using a single reflection.

    Args:
        name: the name of the hkl object to access within the store
        hkl: hkl of the reflection
        pos: position of the reflection
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    Returns:
        miscut angle and miscut axis as a tuple.
    """
    hklcalc = await store.load(name, collection)

    ubcalc: UBCalculation = hklcalc.ubcalc
    try:
        angle, axis = ubcalc.get_miscut_from_hkl(
            (hkl.h, hkl.k, hkl.l), Position(**pos.dict())
        )
    except ValueError:
        raise NoUbMatrixError()

    return angle, axis


#######################################################################################
#                                    U/UB Matrices                                    #
#######################################################################################


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
        3x3 UB matrix in list form

    """
    hklcalc = await store.load(name, collection)

    first_retrieve: Optional[Union[str, int]] = tag1 if tag1 else idx1
    second_retrieve: Optional[Union[str, int]] = tag2 if tag2 else idx2

    hklcalc.ubcalc.calc_ub(first_retrieve, second_retrieve)

    await store.save(name, hklcalc, collection)
    return np.round(hklcalc.ubcalc.UB, 6).tolist()


async def get_ub(
    name: str, store: HklCalcStore, collection: Optional[str]
) -> List[List[float]]:
    """Get the status of the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    Returns:
        a string with the current state of the UB object
    """
    hklcalc = await store.load(name, collection)
    ubcalc: UBCalculation = hklcalc.ubcalc

    if ubcalc.UB is not None:
        return ubcalc.UB.tolist()
    else:
        raise NoUbMatrixError(
            "Cannot retrieve UB matrix. Are you sure it's been set/calculated?"
        )


async def get_u(
    name: str, store: HklCalcStore, collection: Optional[str]
) -> List[List[float]]:
    """Get the status of the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    Returns:
        a string with the current state of the UB object
    """
    hklcalc = await store.load(name, collection)
    ubcalc: UBCalculation = hklcalc.ubcalc

    if ubcalc.U is not None:
        return ubcalc.U.tolist()
    else:
        raise NoUbMatrixError(
            "Cannot retrieve U matrix. Are you sure it's been set/calculated?"
        )


async def set_u(
    name: str,
    u_matrix: List[List[float]],
    store: HklCalcStore,
    collection: Optional[str],
):
    """Manually set the U matrix.

    Args:
        name: the name of the hkl object to access within the store
        u_matrix: 3d array containing the U matrix
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.
    """
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
    """Manually set the UB matrix.

    Args:
        name: the name of the hkl object to access within the store
        ub_matrix: 3d array containing the UB matrix
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.
    """
    hklcalc = await store.load(name, collection)

    ubcalc: UBCalculation = hklcalc.ubcalc
    ubcalc.set_ub(ub_matrix)

    await store.save(name, hklcalc, collection)


#######################################################################################
#                            Surface and Reference Vectors                            #
#######################################################################################


async def set_lab_reference_vector(
    name: str,
    target_value: XyzModel,
    store: HklCalcStore,
    collection: Optional[str],
) -> None:
    """Set the lab reference vector n_phi.

    Args:
        name: the name of the hkl object to access within the store
        target_value: the vector positon in real space
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        None

    """
    hklcalc = await store.load(name, collection)

    ubcalc: UBCalculation = hklcalc.ubcalc
    ubcalc.n_phi = (target_value.x, target_value.y, target_value.z)

    await store.save(name, hklcalc, collection)


async def set_miller_reference_vector(
    name: str,
    target_value: HklModel,
    store: HklCalcStore,
    collection: Optional[str],
) -> None:
    """Set the reference vector n_hkl.

    Args:
        name: the name of the hkl object to access within the store
        target_value: the vector positon in reciprocal space
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        None

    """
    hklcalc = await store.load(name, collection)

    ubcalc: UBCalculation = hklcalc.ubcalc
    ubcalc.n_hkl = (target_value.h, target_value.k, target_value.l)

    await store.save(name, hklcalc, collection)


async def set_lab_surface_normal(
    name: str,
    target_value: XyzModel,
    store: HklCalcStore,
    collection: Optional[str],
):
    """Set the reference vector surf_nphi.

    Args:
        name: the name of the hkl object to access within the store
        target_value: the vector positon in real space
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        None

    """
    hklcalc = await store.load(name, collection)

    ubcalc: UBCalculation = hklcalc.ubcalc
    ubcalc.surf_nphi = (target_value.x, target_value.y, target_value.z)

    await store.save(name, hklcalc, collection)


async def set_miller_surface_normal(
    name: str,
    target_value: HklModel,
    store: HklCalcStore,
    collection: Optional[str],
):
    """Set the reference vector surf_nhkl.

    Args:
        name: the name of the hkl object to access within the store
        target_value: the vector positon in reciprocal space
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        None

    """
    hklcalc = await store.load(name, collection)

    ubcalc: UBCalculation = hklcalc.ubcalc
    ubcalc.surf_nhkl = (target_value.h, target_value.k, target_value.l)

    await store.save(name, hklcalc, collection)


async def get_lab_reference_vector(
    name: str, store: HklCalcStore, collection: Optional[str]
) -> Optional[List[List[float]]]:
    """Get the reference vector nphi.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        Column vector in List[List[float]] format, or None

    """
    hklcalc = await store.load(name, collection)
    ubcalc: UBCalculation = hklcalc.ubcalc

    n_phi = ubcalc.n_phi
    return n_phi.tolist() if n_phi is not None else None


async def get_miller_reference_vector(
    name: str,
    store: HklCalcStore,
    collection,
) -> Optional[List[List[float]]]:
    """Get the reference vector nhkl.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        Column vector in List[List[float]] format, or None

    """
    hklcalc = await store.load(name, collection)
    ubcalc: UBCalculation = hklcalc.ubcalc

    n_hkl = ubcalc.n_hkl
    return n_hkl.tolist() if n_hkl is not None else None


async def get_lab_surface_normal(
    name: str,
    store: HklCalcStore,
    collection,
) -> Optional[List[List[float]]]:
    """Get the surface normal surf_nphi.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        Column vector in List[List[float]] format, or None

    """
    hklcalc = await store.load(name, collection)
    ubcalc: UBCalculation = hklcalc.ubcalc

    surf_nphi = ubcalc.surf_nphi
    return surf_nphi.tolist() if surf_nphi is not None else None


async def get_miller_surface_normal(
    name: str,
    store: HklCalcStore,
    collection,
) -> Optional[List[List[float]]]:
    """Get the surface normal surf_nhkl.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        Column vector in List[List[float]] format, or None

    """
    hklcalc = await store.load(name, collection)
    ubcalc: UBCalculation = hklcalc.ubcalc

    surf_nhkl = ubcalc.surf_nhkl
    return surf_nhkl.tolist() if surf_nhkl is not None else None


#######################################################################################
#                           Vector Calculations in HKL Space                          #
#######################################################################################


async def calculate_vector_from_hkl_and_offset(
    name: str,
    hkl_ref: HklModel,
    polar_angle: float,
    azimuth_angle: float,
    store: HklCalcStore,
    collection,
) -> Tuple[float, float, float]:
    """Calculate a vector in reciprocal space relative to a reference vector.

    Note, this method requires that a UB matrix exists for the Hkl object retrieved.

    Args:
        name: the name of the hkl object to access within the store
        hkl_ref: the reference vector in hkl space
        polar_angle: the polar angle, or the inclination between the zenith and
                     reference vector.
        azimuth_angle: the azimuth angle
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        Tuple[float, float, float]
        The calculated vector, related by an offset to the reference vector given.

    """
    hklcalc = await store.load(name, collection)
    ubcalc: UBCalculation = hklcalc.ubcalc

    if ubcalc.UB is None:
        raise NoUbMatrixError()

    offset_hkl = ubcalc.calc_vector_wrt_hkl_and_offset(
        (hkl_ref.h, hkl_ref.k, hkl_ref.l), polar_angle, azimuth_angle
    )

    return offset_hkl


async def calculate_offset_from_vector_and_hkl(
    name: str,
    hkl_offset: HklModel,
    hkl_ref: HklModel,
    store: HklCalcStore,
    collection,
) -> Tuple[float, float, float]:
    """Calculate angles and magnitude differences between two reciprocal space vectors.

    Note, this method requires that a UB matrix exists for the Hkl object retrieved,
    and that a lattice has been set for it.

    Args:
        name: the name of the hkl object to access within the store.
        hkl_offset: The offset reciprocal space vector.
        hkl_ref: The reference reciprocal space vector.
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        Tuple[float, float, float]
        The offset, in spherical coordinates, between the two reciprocal space vectors,
        containing the polar angle, azimuth angle and magnitude between them.

    """
    hklcalc = await store.load(name, collection)
    ubcalc: UBCalculation = hklcalc.ubcalc

    if ubcalc.UB is None:
        raise NoUbMatrixError()
    if ubcalc.crystal is None:
        raise NoCrystalError()

    if hkl_offset == hkl_ref:
        offset = (0.0, 0.0, 1.0)
    else:
        offset = ubcalc.calc_offset_wrt_vector_and_hkl(
            (hkl_offset.h, hkl_offset.k, hkl_offset.l),
            (hkl_ref.h, hkl_ref.k, hkl_ref.l),
        )

    return offset


#######################################################################################
#                        HKL Solver For Fixed Scattering Vector                       #
#######################################################################################


async def hkl_solver_for_fixed_q(
    name: str,
    hkl: HklModel,
    index_name: str,
    index_value: float,
    a: float,
    b: float,
    c: float,
    d: float,
    store: HklCalcStore,
    collection,
) -> List[Tuple[float, float, float]]:
    """Find valid hkl indices for a fixed scattering vector.

    Note, this method requires that a UB matrix exists for the Hkl object retrieved.
    Coefficients are used to constrain solutions as:
        a*h + b*k + c*l = d

    Args:
        name: the name of the hkl object to access within the store.
        hkl: Reciprocal space vector from which a scattering vector will be calculated.
        index_name: Which miller index to set,
        index_value: value of this miller index.
        a: constraint on the hkl value.
        b: constraint on the hkl value.
        c: constraint on the hkl value.
        d: constraint on the hkl value.
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        List[Tuple[float, float, float]]
        A pair of solutions to the intersection of an ellipsoid with a reference plane.

    """
    hklcalc = await store.load(name, collection)
    ubcalc: UBCalculation = hklcalc.ubcalc

    if ubcalc.UB is None:
        raise NoUbMatrixError()

    q_vector = ubcalc.UB @ np.array([[hkl.h], [hkl.k], [hkl.l]])
    q_value = np.linalg.norm(q_vector) ** 2

    if not ((index_name == "h") or (index_name == "k") or (index_name == "l")):
        raise InvalidIndexError(index_name)

    index_as_literal = cast(Literal["h", "k", "l"], index_name)

    hkl_list = ubcalc.solve_for_hkl_given_fixed_index_and_q(
        index_as_literal, index_value, q_value, a, b, c, d
    )
    return hkl_list
