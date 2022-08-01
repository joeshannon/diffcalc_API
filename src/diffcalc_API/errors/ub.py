from typing import Union

import numpy as np

from diffcalc_API.config import VECTOR_PROPERTIES
from diffcalc_API.errors.definitions import (
    ALL_RESPONSES,
    DiffcalcAPIException,
    ErrorCodesBase,
)


class ErrorCodes(ErrorCodesBase):
    INVALID_SET_LATTICE_PARAMS = 400
    REFERENCE_RETRIEVAL_ERROR = 403
    INVALID_PROPERTY = 400


responses = {code: ALL_RESPONSES[code] for code in np.unique(ErrorCodes.all_codes())}


class InvalidSetLatticeParamsError(DiffcalcAPIException):
    def __init__(self):
        self.detail = ("please provide lattice parameters in request body",)
        self.status_code = ErrorCodes.INVALID_SET_LATTICE_PARAMS


class ReferenceRetrievalError(DiffcalcAPIException):
    def __init__(self, handle: Union[str, int], reference_type: str) -> None:
        self.detail = f"cannot retrieve {reference_type} with tag or index {handle}"
        self.status_code = ErrorCodes.REFERENCE_RETRIEVAL_ERROR


class InvalidPropertyError(DiffcalcAPIException):
    def __init__(self):
        self.detail = f"invalid property. Choose one of: {VECTOR_PROPERTIES}"
        self.status_code = ErrorCodes.INVALID_PROPERTY
