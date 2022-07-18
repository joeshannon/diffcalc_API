from typing import Union

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.ub.reference import Orientation, Reflection

from diffcalc_API.config import vector_properties
from diffcalc_API.errors.definitions import (
    DiffcalcAPIException,
    ErrorCodes,
    all_responses,
)
from diffcalc_API.models.ub import SetLatticeParams


class Codes(ErrorCodes):
    check_params_not_empty = 400
    get_reflection = 403
    get_orientation = 403
    check_property_is_valid = 400


responses = {code: all_responses[code] for code in np.unique(Codes().all_codes())}


def check_params_not_empty(params: SetLatticeParams) -> None:
    non_empty_vars = [var for var, value in params if value is not None]

    if len(non_empty_vars) == 0:
        raise DiffcalcAPIException(
            status_code=Codes.check_params_not_empty,
            detail="please provide parameters in request body",
        )
    return


def get_reflection(hkl: HklCalculation, tag_or_idx: Union[str, int]) -> Reflection:
    try:
        reflection = hkl.ubcalc.get_reflection(tag_or_idx)
    except Exception:
        raise DiffcalcAPIException(
            status_code=Codes.get_reflection,
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
            status_code=Codes.get_orientation,
            detail=(
                "Cannot edit or delete orientation: "
                "No orientation with this tag or index"
            ),
        )

    return orientation


def check_property_is_valid(property: str) -> None:
    if property not in vector_properties:
        raise DiffcalcAPIException(
            status_code=Codes.check_property_is_valid,
            detail=f"invalid property. Choose one of: {vector_properties}",
        )
    return
