from typing import Dict, List, Tuple

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.geometry import Position
from diffcalc.util import DiffcalcException

from diffcalc_API.errorDefinitions import (
    DiffcalcAPIException,
    DiffcalcCoreException,
    ErrorCodes,
    allResponses,
)
from diffcalc_API.models.HklCalculation import positionType


class codes(ErrorCodes):
    check_valid_miller_indices = 400
    check_valid_start_stop_inc = 400
    get_positions = 500


responses = {code: allResponses[code] for code in np.unique(codes().all_codes())}


def check_valid_miller_indices(millerIndices: positionType):
    if sum(millerIndices) == 0:
        raise DiffcalcAPIException(
            status_code=codes.check_valid_miller_indices,
            detail="At least one of the hkl indices must be non-zero",
        )
    return


def check_valid_start_stop_inc(start: float, stop: float, inc: float):
    if len(np.arange(start, stop + inc, inc)) == 0:
        raise DiffcalcAPIException(
            status_code=codes.check_valid_start_stop_inc,
            detail=(
                f"numpy range cannot be formed from start: {start}"
                f" to stop: {stop} in increments of: {inc}"
            ),
        )
    return


def get_positions(
    hklCalc: HklCalculation, millerIndices: positionType, wavelength: float
) -> List[Tuple[Position, Dict[str, float]]]:
    try:
        allPositions = hklCalc.get_position(*millerIndices, wavelength)
    except DiffcalcException as e:
        raise DiffcalcCoreException(
            status_code=codes.get_positions, detail=f"{e.__str__()}"
        )

    return allPositions
