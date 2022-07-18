from typing import Union

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.ub.reference import Orientation, Reflection

from diffcalc_API.config import VECTOR_PROPERTIES
from diffcalc_API.errors.definitions import (
    ALL_RESPONSES,
    DiffcalcAPIException,
    ErrorCodes,
)
from diffcalc_API.models.ub import SetLatticeParams


class Codes(ErrorCodes):
    CHECK_PARAMS_NOT_EMPTY = 400
    GET_REFLECTION = 403
    GET_ORIENTATION = 403
    CHECK_PROPERTY_IS_VALID = 400


responses = {code: ALL_RESPONSES[code] for code in np.unique(Codes().all_codes())}


def check_params_not_empty(params: SetLatticeParams) -> None:
    non_empty_vars = [var for var, value in params if value is not None]

    if len(non_empty_vars) == 0:
        raise DiffcalcAPIException(
            status_code=Codes.CHECK_PARAMS_NOT_EMPTY,
            detail="please provide parameters in request body",
        )


def get_reflection(hkl: HklCalculation, tag_or_idx: Union[str, int]) -> Reflection:
    try:
        reflection = hkl.ubcalc.get_reflection(tag_or_idx)
    except Exception:
        raise DiffcalcAPIException(
            status_code=Codes.GET_REFLECTION,
            detail=(
                "Cannot edit or delete reflection: "
                "No reflection with this tag or index"
            ),
        )

    return reflection


def get_orientation(hkl: HklCalculation, tag_or_idx: Union[str, int]) -> Orientation:
    try:
        orientation = hkl.ubcalc.get_orientation(tag_or_idx)
    except Exception:
        raise DiffcalcAPIException(
            status_code=Codes.GET_ORIENTATION,
            detail=(
                "Cannot edit or delete orientation: "
                "No orientation with this tag or index"
            ),
        )

    return orientation


def check_property_is_valid(property: str) -> None:
    if property not in VECTOR_PROPERTIES:
        raise DiffcalcAPIException(
            status_code=Codes.CHECK_PROPERTY_IS_VALID,
            detail=f"invalid property. Choose one of: {VECTOR_PROPERTIES}",
        )
