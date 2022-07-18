from typing import Optional, Tuple, Union

import numpy as np
from diffcalc.hkl.calc import HklCalculation

from diffcalc_API.errors.definitions import (
    DiffcalcAPIException,
    ErrorCodes,
    all_responses,
)


class Codes(ErrorCodes):
    check_valid_miller_indices = 400
    check_valid_scan_bounds = 400
    calculate_ub_matrix = 400


responses = {code: all_responses[code] for code in np.unique(Codes().all_codes())}


def check_valid_miller_indices(miller_indices: Tuple[float, float, float]) -> None:
    if sum(miller_indices) == 0:
        raise DiffcalcAPIException(
            status_code=Codes.check_valid_miller_indices,
            detail="At least one of the hkl indices must be non-zero",
        )
    return


def check_valid_scan_bounds(start: float, stop: float, inc: float):
    if len(np.arange(start, stop + inc, inc)) == 0:
        raise DiffcalcAPIException(
            status_code=Codes.check_valid_scan_bounds,
            detail=(
                f"numpy range cannot be formed from start: {start}"
                f" to stop: {stop} in increments of: {inc}"
            ),
        )
    return


def calculate_ub_matrix(
    hkl: HklCalculation,
    first_tag: Optional[Union[int, str]],
    second_tag: Optional[Union[int, str]],
) -> None:
    try:
        hkl.ubcalc.calc_ub(first_tag, second_tag)
    except Exception as e:
        raise DiffcalcAPIException(
            status_code=Codes.calculate_ub_matrix,
            detail=f"Error calculating UB matrix: {str(e)}",
        )
    return
