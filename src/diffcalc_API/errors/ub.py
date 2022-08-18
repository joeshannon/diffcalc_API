from typing import Optional, Union

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
    NO_TAG_OR_IDX_PROVIDED = 400
    BOTH_TAG_OR_IDX_PROVIDED = 400


responses = {code: ALL_RESPONSES[code] for code in np.unique(ErrorCodes.all_codes())}


class NoTagOrIdxProvidedError(DiffcalcAPIException):
    def __init__(self):
        self.detail = (
            "One of the following must be provided as a query parameter:"
            + " tag (string), index (integer)"
        )
        self.status_code = ErrorCodes.NO_TAG_OR_IDX_PROVIDED


class BothTagAndIdxProvidedError(DiffcalcAPIException):
    def __init__(self):
        self.detail = (
            "both the tag and index have been provided. These are identifiers"
            + "for a specific orientation or reflection, and so both cannot be"
            + "used. Retry with just one tag or index query parameter."
        )
        self.status_code = ErrorCodes.BOTH_TAG_OR_IDX_PROVIDED


class InvalidSetLatticeParamsError(DiffcalcAPIException):
    def __init__(self):
        self.detail = ("please provide lattice parameters in request body",)
        self.status_code = ErrorCodes.INVALID_SET_LATTICE_PARAMS


class ReferenceRetrievalError(DiffcalcAPIException):
    def __init__(self, handle: Optional[Union[str, int]], reference_type: str) -> None:
        self.detail = f"cannot retrieve {reference_type} with tag or index {handle}"
        self.status_code = ErrorCodes.REFERENCE_RETRIEVAL_ERROR


class InvalidPropertyError(DiffcalcAPIException):
    def __init__(self):
        self.detail = f"invalid property. Choose one of: {VECTOR_PROPERTIES}"
        self.status_code = ErrorCodes.INVALID_PROPERTY
