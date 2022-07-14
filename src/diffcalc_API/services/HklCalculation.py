from itertools import product
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from diffcalc.hkl.geometry import Position

from diffcalc_API.errors.HklCalculation import (
    calculate_UB_matrix,
    check_valid_miller_indices,
    check_valid_scan_bounds,
)
from diffcalc_API.persistence import HklCalcStore

PositionType = Tuple[float, float, float]


async def lab_position_from_miller_indices(
    name: str,
    millerIndices: Tuple[float, float, float],
    wavelength: float,
    store: HklCalcStore,
) -> List[Tuple[Position, Dict[str, float]]]:
    hklCalc = await store.load(name)

    check_valid_miller_indices(millerIndices)
    allPositions = hklCalc.get_position(*millerIndices, wavelength)

    return combine_lab_position_results(allPositions)


async def miller_indices_from_lab_position(
    name: str,
    pos: Tuple[float, float, float, float, float, float],
    wavelength: float,
    store: HklCalcStore,
):
    hklCalc = await store.load(name)
    hklPosition = hklCalc.get_hkl(Position(*pos), wavelength)
    return tuple(np.round(hklPosition, 16))


async def scan_hkl(
    name: str,
    start: PositionType,
    stop: PositionType,
    inc: PositionType,
    wavelength: float,
    store: HklCalcStore,
):
    hklCalc = await store.load(name)
    valueOfAxes = [
        generate_axis(start[i], stop[i], inc[i]) if inc[i] != 0 else [0]
        for i in range(3)
    ]

    results = {}

    for h, k, l in product(*valueOfAxes):
        check_valid_miller_indices((h, k, l))
        allPositions = hklCalc.get_position(h, k, l, wavelength)
        results[f"({h}, {k}, {l})"] = combine_lab_position_results(allPositions)

    return results


async def scan_wavelength(
    name: str,
    start: float,
    stop: float,
    inc: float,
    hkl: PositionType,
    store: HklCalcStore,
):
    hklCalc = await store.load(name)
    check_valid_scan_bounds(start, stop, inc)
    wavelengths = np.arange(start, stop + inc, inc)
    result = {}

    for wavelength in wavelengths:
        allPositions = hklCalc.get_position(*hkl, wavelength)
        result[f"{wavelength}"] = combine_lab_position_results(allPositions)

    return result


async def scan_constraint(
    name: str,
    constraint: str,
    start: float,
    stop: float,
    inc: float,
    hkl: PositionType,
    wavelength: float,
    store: HklCalcStore,
):
    hklCalc = await store.load(name)
    check_valid_scan_bounds(start, stop, inc)
    result = {}
    for value in np.arange(start, stop + inc, inc):
        setattr(hklCalc, constraint, value)
        allPositions = hklCalc.get_position(*hkl, wavelength)
        result[f"{value}"] = combine_lab_position_results(allPositions)

    return result


def generate_axis(start: float, stop: float, inc: float):
    check_valid_scan_bounds(start, stop, inc)
    return np.arange(start, stop + inc, inc)


def combine_lab_position_results(positions: List[Tuple[Position, Dict[str, float]]]):
    result = []

    for position in positions:
        result.append({**position[0].asdict, **position[1]})

    return result


async def calculate_UB(
    name: str,
    firstTag: Optional[Union[int, str]],
    secondTag: Optional[Union[int, str]],
    store: HklCalcStore,
) -> str:
    hklCalc = await store.load(name)

    calculate_UB_matrix(hklCalc, firstTag, secondTag)

    await store.save(name, hklCalc)
    return str(np.round(hklCalc.ubcalc.UB, 6))
