from itertools import product
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from diffcalc.hkl.geometry import Position

from diffcalc_API.errors.hkl import InvalidMillerIndicesError, InvalidScanBoundsError
from diffcalc_API.models.ub import HklModel, PositionModel
from diffcalc_API.stores.protocol import HklCalcStore


async def lab_position_from_miller_indices(
    name: str,
    miller_indices: HklModel,
    wavelength: float,
    store: HklCalcStore,
    collection: Optional[str],
) -> List[Dict[str, float]]:
    hklcalc = await store.load(name, collection)

    if all([idx == 0 for idx in miller_indices]):
        raise InvalidMillerIndicesError()

    all_positions = hklcalc.get_position(*miller_indices.dict().values(), wavelength)

    return combine_lab_position_results(all_positions)


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
    store: HklCalcStore,
    collection: Optional[str],
) -> Dict[str, List[Dict[str, float]]]:
    hklcalc = await store.load(name, collection)

    if (len(start) != 3) or (len(stop) != 3) or (len(inc) != 3):
        raise InvalidMillerIndicesError(
            detail="start, stop and inc must have three floats for each miller index."
        )

    axes_values = [
        generate_axis(start[i], stop[i], inc[i]) if inc[i] != 0 else [0]
        for i in range(3)
    ]

    results = {}

    for h, k, l in product(*axes_values):
        if all([idx == 0 for idx in (h, k, l)]):
            raise InvalidMillerIndicesError()  # what if this goes through 0?

        all_positions = hklcalc.get_position(h, k, l, wavelength)
        results[f"({h}, {k}, {l})"] = combine_lab_position_results(all_positions)

    return results


async def scan_wavelength(
    name: str,
    start: float,
    stop: float,
    inc: float,
    hkl: HklModel,
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
        result[f"{wavelength}"] = combine_lab_position_results(all_positions)

    return result


async def scan_constraint(
    name: str,
    constraint: str,
    start: float,
    stop: float,
    inc: float,
    hkl: HklModel,
    wavelength: float,
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
        result[f"{value}"] = combine_lab_position_results(all_positions)

    return result


def generate_axis(start: float, stop: float, inc: float):
    if len(np.arange(start, stop + inc, inc)) == 0:
        raise InvalidScanBoundsError(start, stop, inc)

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
    collection: Optional[str],
) -> List[List[float]]:
    hklcalc = await store.load(name, collection)

    hklcalc.ubcalc.calc_ub(first_tag, second_tag)

    await store.save(name, hklcalc, collection)
    return np.round(hklcalc.ubcalc.UB, 6).tolist()
