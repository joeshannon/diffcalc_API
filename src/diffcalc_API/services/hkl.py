"""Defines business logic for handling requests from hkl endpoints."""

from itertools import product
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from diffcalc.hkl.geometry import Position

from diffcalc_API.errors.hkl import InvalidMillerIndicesError, InvalidScanBoundsError
from diffcalc_API.models.hkl import SolutionConstraints
from diffcalc_API.models.ub import HklModel, PositionModel
from diffcalc_API.stores.protocol import HklCalcStore


async def lab_position_from_miller_indices(
    name: str,
    miller_indices: HklModel,
    wavelength: float,
    solution_constraints: SolutionConstraints,
    store: HklCalcStore,
    collection: Optional[str],
) -> List[Dict[str, float]]:
    """Convert miller indices to a list of diffractometer positions.

    Args:
        name: the name of the hkl object to access within the store
        miller_indices: miller indices to be converted
        wavelength: wavelength of light used in the experiment
        solution_constraints: object containings angles to constrain solutions by
        store: accessor to the hkl object
        collection: collection within which the hkl object resides

    Returns:
        A list of all possible diffractometer positions
    """
    hklcalc = await store.load(name, collection)

    if all([idx == 0 for idx in miller_indices]):
        raise InvalidMillerIndicesError()

    all_positions = hklcalc.get_position(*miller_indices.dict().values(), wavelength)
    result = combine_lab_position_results(all_positions, solution_constraints)

    return result


async def miller_indices_from_lab_position(
    name: str,
    pos: PositionModel,
    wavelength: float,
    store: HklCalcStore,
    collection: Optional[str],
) -> HklModel:
    """Convert a diffractometer position to a set of miller indices.

    Args:
        name: the name of the hkl object to access within the store
        pos: object containing diffractometer position to be converted.
        wavelength: wavelength of light used in the experiment
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        Object containing converted lab position
    """
    hklcalc = await store.load(name, collection)
    hkl = np.round(hklcalc.get_hkl(Position(**pos.dict()), wavelength), 16)
    return HklModel(h=hkl[0], k=hkl[1], l=hkl[2])


async def scan_hkl(
    name: str,
    start: List[float],
    stop: List[float],
    inc: List[float],
    wavelength: float,
    solution_constraints: SolutionConstraints,
    store: HklCalcStore,
    collection: Optional[str],
) -> Dict[HklModel, List[Dict[str, float]]]:
    """Retrieve possible diffractometer positions for a range of miller indices.

    Args:
        name: the name of the hkl object to access within the store
        start: miller indices to start at
        stop: miller indices to stop at
        inc: miller indices to increment by
        wavelength: wavelength of light used in the experiment
        solution_constraints: object containings angles to constrain solutions by
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        Dictionary of each set of miller indices and their possible diffractometer
        positions.
    """
    hklcalc = await store.load(name, collection)

    if (len(start) != 3) or (len(stop) != 3) or (len(inc) != 3):
        raise InvalidMillerIndicesError(
            "start, stop and inc must have three floats for each miller index."
        )

    axes_values = [
        generate_axis(start[i], stop[i], inc[i]) if inc[i] != 0 else [0]
        for i in range(3)
    ]

    results = {}

    for h, k, l in product(*axes_values):
        if all([idx == 0 for idx in (h, k, l)]):
            raise InvalidMillerIndicesError(
                "choose a hkl range that does not cross through [0, 0, 0]"
            )  # is this good enough? do people need scans through 0,0,0?

        hkl = HklModel(h=h, k=k, l=l)
        all_positions = hklcalc.get_position(h, k, l, wavelength)
        results[hkl] = combine_lab_position_results(all_positions, solution_constraints)

    return results


async def scan_wavelength(
    name: str,
    start: float,
    stop: float,
    inc: float,
    hkl: HklModel,
    solution_constraints: SolutionConstraints,
    store: HklCalcStore,
    collection: Optional[str],
) -> Dict[float, List[Dict[str, float]]]:
    """Retrieve possible diffractometer positions for a range of wavelengths.

    Args:
        name: the name of the hkl object to access within the store
        start: wavelength to start at
        stop: wavelength to stop at
        inc: wavelength to increment by
        hkl: desired miller indices to use for the experiment
        solution_constraints: object containings angles to constrain solutions by
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        Dictionary of each wavelength and the corresponding possible diffractometer
        positions.
    """
    hklcalc = await store.load(name, collection)

    if len(np.arange(start, stop + inc, inc)) == 0:
        raise InvalidScanBoundsError(start, stop, inc)

    wavelengths = np.arange(start, stop + inc, inc)
    result = {}

    for wavelength in wavelengths:
        all_positions = hklcalc.get_position(*hkl.dict().values(), wavelength)
        result[wavelength] = combine_lab_position_results(
            all_positions, solution_constraints
        )

    return result


async def scan_constraint(
    name: str,
    constraint: str,
    start: float,
    stop: float,
    inc: float,
    hkl: HklModel,
    wavelength: float,
    solution_constraints: SolutionConstraints,
    store: HklCalcStore,
    collection: Optional[str],
) -> Dict[float, List[Dict[str, float]]]:
    """Retrieve possible diffractometer positions while scanning across a constraint.

    Args:
        name: the name of the hkl object to access within the store
        constraint: the name of the constraint to use.
        start: constraint to start at
        stop: constraint to stop at
        inc: constraint to increment by
        hkl: desired miller indices to use for the experiment
        wavelength: wavelength of light used in the experiment
        solution_constraints: object containings angles to constrain solutions by
        store: accessor to the hkl object.
        collection: collection within which the hkl object resides.

    Returns:
        Dictionary of each constraint value and the corresponding possible
        diffractometer positions.
    """
    hklcalc = await store.load(name, collection)

    if len(np.arange(start, stop + inc, inc)) == 0:
        raise InvalidScanBoundsError(start, stop, inc)

    result = {}
    for value in np.arange(start, stop + inc, inc):
        setattr(hklcalc, constraint, value)
        all_positions = hklcalc.get_position(*hkl.dict().values(), wavelength)
        result[value] = combine_lab_position_results(
            all_positions, solution_constraints
        )

    return result


def generate_axis(start: float, stop: float, inc: float):
    """Attempt to generate a numpy range between values.

    Args:
        start: value to start at
        stop: value to stop at
        inc: value to increment by

    Returns:
        a numpy range.

    Throws an error if the numpy range is null, most likely due to non-logical
    range like 0->1 in increments of a negative number.
    """
    if len(np.arange(start, stop + inc, inc)) == 0:
        raise InvalidScanBoundsError(start, stop, inc)

    return np.arange(start, stop + inc, inc)


def combine_lab_position_results(
    positions: List[Tuple[Position, Dict[str, float]]],
    solution_constraints: SolutionConstraints,
) -> List[Dict[str, float]]:
    """Combine physical and virtual angles.

    Args:
        positions: list of each set of physical and virtual angles.
        solution_constraints: object containings angles to constrain solutions by

    Returns:
        a list of angles, combined together into one dictionary.

    """
    axes = solution_constraints.axes
    low_bound = solution_constraints.low_bound
    high_bound = solution_constraints.high_bound

    result = []

    for position in positions:
        physical_angles, virtual_angles = position
        if axes and low_bound and high_bound:
            if all(
                [
                    low_bound[i] < getattr(physical_angles, angle) < high_bound[i]
                    for i, angle in enumerate(axes)
                ]
            ):
                result.append({**physical_angles.asdict, **virtual_angles})
        else:
            result.append({**physical_angles.asdict, **virtual_angles})

    return result


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
