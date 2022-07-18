from itertools import product
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from diffcalc.hkl.geometry import Position

from diffcalc_API.errors.hkl import (
    calculate_ub_matrix,
    check_valid_miller_indices,
    check_valid_scan_bounds,
)
from diffcalc_API.stores.protocol import HklCalcStore

PositionType = Tuple[float, float, float]


async def lab_position_from_miller_indices(
    name: str,
    miller_indices: Tuple[float, float, float],
    wavelength: float,
    store: HklCalcStore,
) -> List[Dict[str, float]]:
    hklcalc = await store.load(name)

    check_valid_miller_indices(miller_indices)
    all_positions = hklcalc.get_position(*miller_indices, wavelength)

    return combine_lab_position_results(all_positions)


async def miller_indices_from_lab_position(
    name: str,
    pos: Tuple[float, float, float, float, float, float],
    wavelength: float,
    store: HklCalcStore,
) -> Tuple[Any, ...]:
    hklcalc = await store.load(name)
    position = hklcalc.get_hkl(Position(*pos), wavelength)
    return tuple(np.round(position, 16))


async def scan_hkl(
    name: str,
    start: PositionType,
    stop: PositionType,
    inc: PositionType,
    wavelength: float,
    store: HklCalcStore,
) -> Dict[str, List[Dict[str, float]]]:
    hklcalc = await store.load(name)
    axes_values = [
        generate_axis(start[i], stop[i], inc[i]) if inc[i] != 0 else [0]
        for i in range(3)
    ]

    results = {}

    for h, k, l in product(*axes_values):
        check_valid_miller_indices((h, k, l))
        all_positions = hklcalc.get_position(h, k, l, wavelength)
        results[f"({h}, {k}, {l})"] = combine_lab_position_results(all_positions)

    return results


async def scan_wavelength(
    name: str,
    start: float,
    stop: float,
    inc: float,
    hkl: PositionType,
    store: HklCalcStore,
) -> Dict[str, List[Dict[str, float]]]:
    hklcalc = await store.load(name)
    check_valid_scan_bounds(start, stop, inc)
    wavelengths = np.arange(start, stop + inc, inc)
    result = {}

    for wavelength in wavelengths:
        all_positions = hklcalc.get_position(*hkl, wavelength)
        result[f"{wavelength}"] = combine_lab_position_results(all_positions)

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
) -> Dict[str, List[Dict[str, float]]]:
    hklcalc = await store.load(name)
    check_valid_scan_bounds(start, stop, inc)
    result = {}
    for value in np.arange(start, stop + inc, inc):
        setattr(hklcalc, constraint, value)
        all_positions = hklcalc.get_position(*hkl, wavelength)
        result[f"{value}"] = combine_lab_position_results(all_positions)

    return result


def generate_axis(start: float, stop: float, inc: float):
    check_valid_scan_bounds(start, stop, inc)
    return np.arange(start, stop + inc, inc)


def combine_lab_position_results(
    positions: List[Tuple[Position, Dict[str, float]]]
) -> List[Dict[str, float]]:
    result = []

    for position in positions:
        result.append({**position[0].asdict, **position[1]})

    return result


async def calculate_ub(
    name: str,
    first_tag: Optional[Union[int, str]],
    second_tag: Optional[Union[int, str]],
    store: HklCalcStore,
) -> str:
    hklcalc = await store.load(name)

    calculate_ub_matrix(hklcalc, first_tag, second_tag)

    await store.save(name, hklcalc)
    return str(np.round(hklcalc.ubcalc.UB, 6))
