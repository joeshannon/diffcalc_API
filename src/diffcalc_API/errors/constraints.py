import numpy as np

from diffcalc_API.config import ALL_CONSTRAINTS
from diffcalc_API.errors.definitions import (
    ALL_RESPONSES,
    DiffcalcAPIException,
    ErrorCodesBase,
)


class ErrorCodes(ErrorCodesBase):
    INVALID_CONSTRAINT = 400


responses = {code: ALL_RESPONSES[code] for code in np.unique(ErrorCodes.all_codes())}


class InvalidConstraintError(DiffcalcAPIException):
    def __init__(self, constraint: str):
        self.detail = (
            f"property {constraint} does not exist as a valid constraint."
            f" Valid constraints are: {ALL_CONSTRAINTS}"
        )
        self.status_code = ErrorCodes.INVALID_CONSTRAINT
