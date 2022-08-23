from itertools import product
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from diffcalc.hkl.geometry import Position

from diffcalc_API.errors.hkl import InvalidMillerIndicesError, InvalidScanBoundsError
from diffcalc_API.models.hkl import SolutionConstraints
from diffcalc_API.models.ub import HklModel, PositionModel
from diffcalc_API.stores.protocol import HklCalcStore
from diffcalc_API.utils import async_wrap


async def lab_position_from_miller_indices(
    name: str,
    miller_indices: HklModel,
    wavelength: float,
    solution_constraints: SolutionConstraints,
    store: HklCalcStore,
    collection: Optional[str],
) -> List[Dict[str, float]]:
    hklcalc = await store.load(name, collection)

    if all([idx == 0 for idx in miller_indices]):
        raise InvalidMillerIndicesError()

    all_positions = hklcalc.get_position(*miller_indices.dict().values(), wavelength)
    result = await combine_lab_position_results(all_positions, solution_constraints)

    return result


async def miller_indices_from_lab_position(
    name: str,
    pos: PositionModel,
    wavelength: float,
    store: HklCalcStore,
    collection: Optional[str],
) -> HklModel:
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
) -> Dict[str, List[Dict[str, float]]]:
    hklcalc = await store.load(name, collection)

    if (len(start) != 3) or (len(stop) != 3) or (len(inc) != 3):
        raise InvalidMillerIndicesError(
            "start, stop and inc must have three floats for each miller index."
        )

    axes_values = [
        await generate_axis(start[i], stop[i], inc[i]) if inc[i] != 0 else [0]
        for i in range(3)
    ]

    results = {}

    for h, k, l in product(*axes_values):
        if all([idx == 0 for idx in (h, k, l)]):
            raise InvalidMillerIndicesError(
                "choose a hkl range that does not cross through [0, 0, 0]"
            )  # is this good enough? do people need scans through 0,0,0?

        all_positions = hklcalc.get_position(h, k, l, wavelength)
        results[f"({h}, {k}, {l})"] = await combine_lab_position_results(
            all_positions, solution_constraints
        )

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
) -> Dict[str, List[Dict[str, float]]]:
    hklcalc = await store.load(name, collection)

    if len(np.arange(start, stop + inc, inc)) == 0:
        raise InvalidScanBoundsError(start, stop, inc)

    wavelengths = np.arange(start, stop + inc, inc)
    result = {}

    for wavelength in wavelengths:
        all_positions = hklcalc.get_position(*hkl.dict().values(), wavelength)
        result[f"{wavelength}"] = await combine_lab_position_results(
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
) -> Dict[str, List[Dict[str, float]]]:
    hklcalc = await store.load(name, collection)

    if len(np.arange(start, stop + inc, inc)) == 0:
        raise InvalidScanBoundsError(start, stop, inc)

    result = {}
    for value in np.arange(start, stop + inc, inc):
        setattr(hklcalc, constraint, value)
        all_positions = hklcalc.get_position(*hkl.dict().values(), wavelength)
        result[f"{value}"] = await combine_lab_position_results(
            all_positions, solution_constraints
        )

    return result


@async_wrap
def generate_axis(start: float, stop: float, inc: float):
    if len(np.arange(start, stop + inc, inc)) == 0:
        raise InvalidScanBoundsError(start, stop, inc)

    return np.arange(start, stop + inc, inc)


@async_wrap
def combine_lab_position_results(
    positions: List[Tuple[Position, Dict[str, float]]],
    solution_constraints: SolutionConstraints,
) -> List[Dict[str, float]]:
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
    hklcalc = await store.load(name, collection)

    first_retrieve: Optional[Union[str, int]] = tag1 if tag1 else idx1
    second_retrieve: Optional[Union[str, int]] = tag2 if tag2 else idx2

    hklcalc.ubcalc.calc_ub(first_retrieve, second_retrieve)

    await store.save(name, hklcalc, collection)
    return np.round(hklcalc.ubcalc.UB, 6).tolist()
