"""Endpoints relating to the management of setting up the UB calculation."""

from typing import List, Optional, Union

from fastapi import APIRouter, Body, Depends, Query

from diffcalc_api.errors.ub import (
    BothTagAndIdxProvidedError,
    InvalidSetLatticeParamsError,
    NoTagOrIdxProvidedError,
)
from diffcalc_api.examples import ub as examples
from diffcalc_api.models.response import (
    ArrayResponse,
    CoordinateResponse,
    InfoResponse,
    MiscutResponse,
    StringResponse,
)
from diffcalc_api.models.ub import (
    AddOrientationParams,
    AddReflectionParams,
    EditOrientationParams,
    EditReflectionParams,
    HklModel,
    MiscutModel,
    PositionModel,
    SetLatticeParams,
    SphericalCoordinates,
    XyzModel,
    select_idx_or_tag_str,
)
from diffcalc_api.services import ub as service
from diffcalc_api.stores.protocol import HklCalcStore, get_store

router = APIRouter(prefix="/ub", tags=["ub"])


@router.get("/{name}/status", response_model=StringResponse)
async def get_ub_status(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Get the status of the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    Returns:
        a string with the current state of the UB object
    """
    content = await service.get_ub_status(name, store, collection)
    return StringResponse(payload=content)


#######################################################################################
#                                     Reflections                                     #
#######################################################################################


@router.post("/{name}/reflection", response_model=InfoResponse)
async def add_reflection(
    name: str,
    params: AddReflectionParams = Body(..., example=examples.add_reflection),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
    tag: Optional[str] = Query(default=None, example="refl1"),
):
    """Add reflection to the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        params: detail about the reflection object to be added
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to attribute to the new reflection

    """
    await service.add_reflection(name, params, store, collection, tag)
    return InfoResponse(
        message=(
            f"added reflection for UB Calculation of crystal {name} in "
            + f"collection {collection}"
        )
    )


@router.put("/{name}/reflection", response_model=InfoResponse)
async def edit_reflection(
    name: str,
    params: EditReflectionParams = Body(..., example=examples.edit_reflection),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
    tag: Optional[str] = Query(default=None, example="refl1"),
    idx: Optional[int] = Query(default=None),
):
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
    if (tag is None) and (idx is None):
        raise NoTagOrIdxProvidedError()

    if (tag is not None) and (idx is not None):
        raise BothTagAndIdxProvidedError()

    await service.edit_reflection(name, params, store, collection, tag, idx)
    return InfoResponse(
        message=(
            f"reflection of crystal {name} in collection {collection} with "
            + f"{select_idx_or_tag_str(idx, tag)} edited"
        )
    )


@router.delete("/{name}/reflection", response_model=InfoResponse)
async def delete_reflection(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
    tag: Optional[str] = Query(default=None, example="refl1"),
    idx: Optional[int] = Query(default=None),
):
    """Delete reflection in the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to retrieve the reflection by
        idx: optional index to retrieve the reflection by

    Exactly one tag or index must be provided.
    """
    if (idx is None) and (tag is None):
        raise NoTagOrIdxProvidedError()
    if (idx is not None) and (tag is not None):
        raise BothTagAndIdxProvidedError()

    await service.delete_reflection(name, store, collection, tag, idx)
    return InfoResponse(
        message=(
            f"reflection of crystal {name} in collection {collection} "
            + f"with {select_idx_or_tag_str(idx, tag)} deleted"
        )
    )


#######################################################################################
#                                    Orientations                                     #
#######################################################################################


@router.post("/{name}/orientation", response_model=InfoResponse)
async def add_orientation(
    name: str,
    params: AddOrientationParams = Body(..., example=examples.add_orientation),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
    tag: Optional[str] = Query(default=None, example="plane"),
):
    """Add orientation to the UB object in the hkl object.

    Args:
        name: the name of the hkl object to access within the store
        params: detail about the orientation object to be added
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to attribute to the new orientation

    """
    await service.add_orientation(name, params, store, collection, tag)
    return InfoResponse(
        message=(
            f"added orientation for UB Calculation of crystal {name} in "
            + f"collection {collection}"
        )
    )


@router.put("/{name}/orientation", response_model=InfoResponse)
async def edit_orientation(
    name: str,
    params: EditOrientationParams = Body(..., example=examples.edit_orientation),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
    tag: Optional[str] = Query(default=None),
    idx: Optional[int] = Query(default=None, example=0),
):
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
    if (idx is None) and (tag is None):
        raise NoTagOrIdxProvidedError()
    if (idx is not None) and (tag is not None):
        raise BothTagAndIdxProvidedError()

    await service.edit_orientation(name, params, store, collection, tag, idx)
    return InfoResponse(
        message=(
            f"orientation of crystal {name} in collection {collection} with "
            f"{select_idx_or_tag_str(idx, tag)} edited"
        )
    )


@router.delete("/{name}/orientation", response_model=InfoResponse)
async def delete_orientation(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
    tag: Optional[str] = Query(default=None, example="plane"),
    idx: Optional[int] = Query(default=None),
):
    """Delete orientation in the UB object in a given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
        tag: optional tag to retrieve the orientation by
        idx: optional index to retrieve the orientation by

    Exactly one tag or index must be provided.
    """
    if (idx is None) and (tag is None):
        raise NoTagOrIdxProvidedError()
    if (idx is not None) and (tag is not None):
        raise BothTagAndIdxProvidedError()

    await service.delete_orientation(name, store, collection, tag, idx)
    return InfoResponse(
        message=(
            f"orientation of crystal {name} in collection {collection} "
            + f"with {select_idx_or_tag_str(idx, tag)} deleted"
        )
    )


#######################################################################################
#                                       Crystal                                       #
#######################################################################################


@router.patch("/{name}/lattice", response_model=InfoResponse)
async def set_lattice(
    name: str,
    params: SetLatticeParams = Body(example=examples.set_lattice),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Set the Crystal parameters in the UB object in a given hkl object.

    Args:
        name: the name of the hkl object to access within the store
        params: the parameters to use to set the lattice
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    """
    non_empty_vars = [var for var, value in params if value is not None]

    if len(non_empty_vars) == 0:
        raise InvalidSetLatticeParamsError()

    await service.set_lattice(name, params, store, collection)
    return InfoResponse(
        message=(
            f"lattice has been set for UB calculation of crystal {name} in "
            + f"collection {collection}"
        )
    )


#######################################################################################
#                                       Miscuts                                       #
#######################################################################################


@router.put("/{name}/miscut", response_model=InfoResponse)
async def set_miscut(
    name: str,
    rot_axis: XyzModel = Body(...),
    angle: float = Query(...),
    add_miscut: bool = Query(default=False),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Find the U matrix using a miscut axis/angle, and set this as the new U matrix.

    Args:
        name: the name of the hkl object to access within the store
        rot_axis: the rotational axis of the miscut
        angle: the miscut angle
        add_miscut: boolean determining extra processing on U matrix before it is set
        store: accessor to the hkl object
        collection: collection within which the hkl object resides
    """
    await service.set_miscut(name, rot_axis, angle, add_miscut, store, collection)
    return InfoResponse(
        message=(
            "Miscut has been set using the provided rotation axis and angle of the "
            + f"miscut for crystal {name} of collection {collection}."
        )
    )


@router.get("/{name}/miscut", response_model=MiscutResponse)
async def get_miscut(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Get the rotation axis and angle of the miscut, using current UB matrix.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    Returns:
        miscut angle and miscut axis as a list.
    """
    angle, axis = await service.get_miscut(name, store, collection)
    return MiscutResponse(
        payload=MiscutModel(
            angle=angle, rotation_axis=XyzModel(x=axis[0], y=axis[1], z=axis[2])
        )
    )


@router.get("/{name}/miscut/hkl", response_model=MiscutResponse)
async def get_miscut_from_hkl(
    name: str,
    hkl: HklModel = Depends(),
    pos: PositionModel = Depends(),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
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
    angle, axis = await service.get_miscut_from_hkl(name, hkl, pos, store, collection)
    return MiscutResponse(
        payload=MiscutModel(
            angle=angle, rotation_axis=XyzModel(x=axis[0], y=axis[1], z=axis[2])
        )
    )


#######################################################################################
#                                    U/UB Matrices                                    #
#######################################################################################


@router.get("/{name}/calculate", response_model=ArrayResponse)
async def calculate_ub(
    name: str,
    tag1: Optional[str] = Query(default=None, example="refl1"),
    idx1: Optional[int] = Query(default=None),
    tag2: Optional[str] = Query(default=None, example="plane"),
    idx2: Optional[int] = Query(default=None),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
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
        ArrayResponse object containing a list of angles, combined together into one
        dictionary.

    """
    content = await service.calculate_ub(
        name, store, collection, tag1, idx1, tag2, idx2
    )
    return ArrayResponse(payload=content)


@router.put("/{name}/ub", response_model=InfoResponse)
async def set_ub(
    name: str,
    ub_matrix: List[List[float]] = Body(
        ..., example=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    ),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Manually set the UB matrix.

    Args:
        name: the name of the hkl object to access within the store
        u_matrix: 3d array containing the UB matrix
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.
    """
    await service.set_ub(name, ub_matrix, store, collection)
    return InfoResponse(
        message=f"UB matrix set for crystal {name} of collection {collection}"
    )


@router.put("/{name}/u", response_model=InfoResponse)
async def set_u(
    name: str,
    u_matrix: List[List[float]] = Body(
        ..., example=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    ),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Manually set the U matrix.

    Args:
        name: the name of the hkl object to access within the store
        u_matrix: 3d array containing the U matrix
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.
    """
    await service.set_u(name, u_matrix, store, collection)
    return InfoResponse(
        message=f"U matrix set for crystal {name} of collection {collection}"
    )


@router.get("/{name}/ub", response_model=ArrayResponse)
async def get_ub(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Get the UB matrix.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        ArrayResponse object with the UB matrix as an array.

    """
    content = await service.get_ub(name, store, collection)
    return ArrayResponse(payload=content)


@router.get("/{name}/u", response_model=ArrayResponse)
async def get_u(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Get the U matrix.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        ArrayResponse object with the U matrix as an array.

    """
    content = await service.get_u(name, store, collection)
    return ArrayResponse(payload=content)


#######################################################################################
#                            Surface and Reference Vectors                            #
#######################################################################################


@router.put("/{name}/nphi", response_model=InfoResponse)
async def set_lab_reference_vector(
    name: str,
    target_value: XyzModel = Body(..., example={"x": 1, "y": 0, "z": 0}),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Set the lab reference vector n_phi.

    Args:
        name: the name of the hkl object to access within the store
        target_value: the vector positon in real space
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        InfoResponse describing the vector has been set successfully.

    """
    await service.set_lab_reference_vector(name, target_value, store, collection)
    return InfoResponse(
        message=f"Reference vector set for crystal {name} of collection {collection}"
    )


@router.put("/{name}/nhkl", response_model=InfoResponse)
async def set_miller_reference_vector(
    name: str,
    target_value: HklModel = Body(..., example={"h": 1, "k": 0, "l": 0}),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Set the reference vector n_hkl.

    Args:
        name: the name of the hkl object to access within the store
        target_value: the vector positon in reciprocal space
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        InfoResponse describing the vector has been set successfully.

    """
    await service.set_miller_reference_vector(name, target_value, store, collection)
    return InfoResponse(
        message=f"Reference vector set for crystal {name} of collection {collection}"
    )


@router.put("/{name}/surface/nphi", response_model=InfoResponse)
async def set_lab_surface_normal(
    name: str,
    target_value: XyzModel = Body(..., example={"x": 1, "y": 0, "z": 0}),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Set the reference vector surf_nphi.

    Args:
        name: the name of the hkl object to access within the store
        target_value: the vector positon in real space
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        InfoResponse describing the vector has been set successfully.

    """
    await service.set_lab_surface_normal(name, target_value, store, collection)
    return InfoResponse(
        message=f"Surface normal set for crystal {name} of collection {collection}"
    )


@router.put("/{name}/surface/nhkl", response_model=InfoResponse)
async def set_miller_surface_normal(
    name: str,
    target_value: HklModel = Body(..., example={"h": 1, "k": 0, "l": 0}),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Set the reference vector surf_nhkl.

    Args:
        name: the name of the hkl object to access within the store
        target_value: the vector positon in reciprocal space
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        InfoResponse describing the vector has been set successfully.

    """
    await service.set_miller_surface_normal(name, target_value, store, collection)
    return InfoResponse(
        message=f"Surface normal set for crystal {name} of collection {collection}"
    )


@router.get("/{name}/nphi", response_model=Union[ArrayResponse, InfoResponse])
async def get_lab_reference_vector(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Get the reference vector nphi.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        ArrayResponse with the vector, or
        InfoResponse if it doesn't exist

    """
    lab_vector: Optional[List[List[float]]] = await service.get_lab_reference_vector(
        name, store, collection
    )
    if lab_vector is not None:
        return ArrayResponse(payload=lab_vector)
    else:
        return InfoResponse(message="This vector does not exist.")


@router.get("/{name}/nhkl", response_model=Union[ArrayResponse, InfoResponse])
async def get_miller_reference_vector(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Get the reference vector nhkl.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        ArrayResponse with the vector, or
        InfoResponse if it doesn't exist

    """
    lab_vector: Optional[List[List[float]]] = await service.get_miller_reference_vector(
        name, store, collection
    )
    if lab_vector is not None:
        return ArrayResponse(payload=lab_vector)
    else:
        return InfoResponse(message="This vector does not exist.")


@router.get("/{name}/surface/nphi", response_model=Union[ArrayResponse, InfoResponse])
async def get_lab_surface_normal(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Get the surface normal surf_nphi.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        ArrayResponse with the vector, or
        InfoResponse if it doesn't exist

    """
    lab_vector: Optional[List[List[float]]] = await service.get_lab_surface_normal(
        name, store, collection
    )
    if lab_vector is not None:
        return ArrayResponse(payload=lab_vector)
    else:
        return InfoResponse(message="This vector does not exist.")


@router.get("/{name}/surface/nhkl", response_model=Union[ArrayResponse, InfoResponse])
async def get_miller_surface_normal(
    name: str,
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Get the surface normal surf_nhkl.

    Args:
        name: the name of the hkl object to access within the store
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        ArrayResponse with the vector, or
        InfoResponse if it doesn't exist

    """
    lab_vector: Optional[List[List[float]]] = await service.get_miller_surface_normal(
        name, store, collection
    )
    if lab_vector is not None:
        return ArrayResponse(payload=lab_vector)
    else:
        return InfoResponse(message="This vector does not exist.")


#######################################################################################
#                           Vector Calculations in HKL Space                          #
#######################################################################################


@router.get("/{name}/vector", response_model=CoordinateResponse)
async def calculate_vector_from_hkl_and_offset(
    name: str,
    hkl_ref: HklModel = Depends(),
    polar_angle: float = Query(..., example=45.0),
    azimuth_angle: float = Query(..., example=45.0),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
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
        CoordinateResponse
        Containing the calculated reciprocal space vector as h, k, l indices.

    """
    vector = await service.calculate_vector_from_hkl_and_offset(
        name, hkl_ref, polar_angle, azimuth_angle, store, collection
    )

    return CoordinateResponse(payload=HklModel(h=vector[0], k=vector[1], l=vector[2]))


@router.get("/{name}/offset", response_model=CoordinateResponse)
async def calculate_offset_from_vector_and_hkl(
    name: str,
    h1: float = Query(..., example=0.0),
    k1: float = Query(..., example=1.0),
    l1: float = Query(..., example=0.0),
    h2: float = Query(..., example=1.0),
    k2: float = Query(..., example=0.0),
    l2: float = Query(..., example=0.0),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    """Calculate angles and magnitude differences between two reciprocal space vectors.

    Note, this method requires that a UB matrix exists for the Hkl object retrieved,
    and that a lattice has been set for it.

    Args:
        name: the name of the hkl object to access within the store
        h1: h index of the reference vector
        k1: k index of the reference vector
        l1: l index of the reference vector
        h2: h index of the vector relative to which the offset should be calculated
        k2: k index of the vector relative to which the offset should be calculated
        l2: l index of the vector relative to which the offset should be calculated
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        CoordinateResponse
        The offset, in spherical coordinates, between the two reciprocal space vectors,
        containing the polar angle, azimuth angle and magnitude between them.

    """
    hkl_ref = HklModel(h=h1, k=k1, l=l1)
    hkl_offset = HklModel(h=h2, k=k2, l=l2)

    vector = await service.calculate_offset_from_vector_and_hkl(
        name, hkl_offset, hkl_ref, store, collection
    )

    return CoordinateResponse(
        payload=SphericalCoordinates(
            polar_angle=vector[0], azimuth_angle=vector[1], magnitude=vector[2]
        )
    )


#######################################################################################
#                        HKL Solver For Fixed Scattering Vector                       #
#######################################################################################


@router.get("/{name}/solve/hkl/fixed/q", response_model=ArrayResponse)
async def hkl_solver_for_fixed_q(
    name: str,
    hkl: HklModel = Depends(),
    index_name: str = Query(..., example="h"),
    index_value: float = Query(..., example=0.0),
    a: float = Query(..., example=0.0),
    b: float = Query(..., example=1.0),
    c: float = Query(..., example=0.0),
    d: float = Query(..., example=0.25),
    store: HklCalcStore = Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
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
        ArrayResponse
        A list of lists, with each sublist being a solution.

    """
    hkl_list = await service.hkl_solver_for_fixed_q(
        name, hkl, index_name, index_value, a, b, c, d, store, collection
    )
    hkl_list_as_list_of_lists = [list(i) for i in hkl_list]

    return ArrayResponse(payload=hkl_list_as_list_of_lists)
