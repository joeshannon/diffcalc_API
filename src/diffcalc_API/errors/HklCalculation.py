from typing import Optional, Tuple, Union

import numpy as np
from diffcalc.hkl.calc import HklCalculation

from diffcalc_API.errors.definitions import (
    DiffcalcAPIException,
    ErrorCodes,
    allResponses,
)


class codes(ErrorCodes):
    check_valid_miller_indices = 400
    check_valid_scan_bounds = 400
    calculate_UB_matrix = 400


responses = {code: allResponses[code] for code in np.unique(codes().all_codes())}


def check_valid_miller_indices(millerIndices: Tuple[float, float, float]) -> None:
    if sum(millerIndices) == 0:
        raise DiffcalcAPIException(
            status_code=codes.check_valid_miller_indices,
            detail="At least one of the hkl indices must be non-zero",
        )
    return


def check_valid_scan_bounds(start: float, stop: float, inc: float):
    if len(np.arange(start, stop + inc, inc)) == 0:
        raise DiffcalcAPIException(
            status_code=codes.check_valid_scan_bounds,
            detail=(
                f"numpy range cannot be formed from start: {start}"
                f" to stop: {stop} in increments of: {inc}"
            ),
        )
    return


def calculate_UB_matrix(
    hkl: HklCalculation,
    firstTag: Optional[Union[int, str]],
    secondTag: Optional[Union[int, str]],
) -> None:
    try:
        hkl.ubcalc.calc_ub(firstTag, secondTag)
    except Exception as e:
        raise DiffcalcAPIException(
            status_code=codes.calculate_UB_matrix,
            detail=f"Error calculating UB matrix: {str(e)}",
        )
    return
