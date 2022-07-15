from typing import Union

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.ub.reference import Orientation, Reflection

from diffcalc_API.config import VectorProperties
from diffcalc_API.errors.definitions import (
    DiffcalcAPIException,
    ErrorCodes,
    allResponses,
)
from diffcalc_API.models.UBCalculation import setLatticeParams


class codes(ErrorCodes):
    check_params_not_empty = 400
    get_reflection = 403
    get_orientation = 403
    check_property_is_valid = 400


responses = {code: allResponses[code] for code in np.unique(codes().all_codes())}


def check_params_not_empty(params: setLatticeParams) -> None:
    nonEmptyVariables = [var for var, value in params if value is not None]

    if len(nonEmptyVariables) == 0:
        raise DiffcalcAPIException(
            status_code=codes.check_params_not_empty,
            detail="please provide parameters in request body",
        )
    return


def get_reflection(hkl: HklCalculation, tagOrIdx: Union[str, int]) -> Reflection:
    try:
        reflection = hkl.ubcalc.get_reflection(tagOrIdx)
    except Exception:
        raise DiffcalcAPIException(
            status_code=codes.get_reflection,
            detail=(
                "Cannot edit or delete reflection: "
                "No reflection with this tag or index"
            ),
        )

    return reflection


def get_orientation(hkl: HklCalculation, tagOrIdx: Union[str, int]) -> Orientation:
    try:
        orientation = hkl.ubcalc.get_orientation(tagOrIdx)
    except Exception:
        raise DiffcalcAPIException(
            status_code=codes.get_orientation,
            detail=(
                "Cannot edit or delete orientation: "
                "No orientation with this tag or index"
            ),
        )

    return orientation


def check_property_is_valid(property: str) -> None:
    if property not in VectorProperties:
        raise DiffcalcAPIException(
            status_code=codes.check_property_is_valid,
            detail=f"invalid property. Choose one of: {VectorProperties}",
        )
    return
