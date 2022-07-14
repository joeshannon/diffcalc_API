from itertools import product
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.geometry import Position

from diffcalc_API.errors.HklCalculation import (
    calculate_UB_matrix,
    check_valid_miller_indices,
    check_valid_scan_bounds,
)

PositionType = Tuple[float, float, float]


def lab_position_from_miller_indices(
    millerIndices: Tuple[float, float, float],
    wavelength: float,
    hklCalc: HklCalculation,
) -> List[Tuple[Position, Dict[str, float]]]:
    check_valid_miller_indices(millerIndices)
    allPositions = hklCalc.get_position(*millerIndices, wavelength)

    return combine_lab_position_results(allPositions)


def miller_indices_from_lab_position(
    pos: Tuple[float, float, float, float, float, float],
    wavelength: float,
    hklCalc: HklCalculation,
):
    hklPosition = hklCalc.get_hkl(Position(*pos), wavelength)
    return tuple(np.round(hklPosition, 16))


def scan_hkl(
    start: PositionType,
    stop: PositionType,
    inc: PositionType,
    wavelength: float,
    hklCalc: HklCalculation,
):
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


def scan_wavelength(
    start: float,
    stop: float,
    inc: float,
    hkl: PositionType,
    hklCalc: HklCalculation,
):
    check_valid_scan_bounds(start, stop, inc)
    wavelengths = np.arange(start, stop + inc, inc)
    result = {}

    for wavelength in wavelengths:
        allPositions = hklCalc.get_position(*hkl, wavelength)
        result[f"{wavelength}"] = combine_lab_position_results(allPositions)

    return result


def scan_constraint(
    constraint: str,
    start: float,
    stop: float,
    inc: float,
    hkl: PositionType,
    wavelength: float,
    hklCalc: HklCalculation,
):
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


def calculate_UB(
    name: str,
    firstTag: Optional[Union[int, str]],
    secondTag: Optional[Union[int, str]],
    hklCalc: HklCalculation,
    persist: Callable[[HklCalculation, str], Path],
):
    calculate_UB_matrix(hklCalc, firstTag, secondTag)
    persist(hklCalc, name)
