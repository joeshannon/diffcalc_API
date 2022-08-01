import numpy as np

from diffcalc_API.config import ALL_CONSTRAINTS
from diffcalc_API.errors.definitions import (
    ALL_RESPONSES,
    DiffcalcAPIException,
    ErrorCodes,
)


class Codes(ErrorCodes):
    INVALID_CONSTRAINT_ERROR = 400


responses = {code: ALL_RESPONSES[code] for code in np.unique(Codes.all_codes())}


class InvalidConstraintError(DiffcalcAPIException):
    def __init__(self, constraint: str):
        self.detail = (
            f"property {constraint} does not exist as a valid constraint."
            f" Choose one of {ALL_CONSTRAINTS}"
        )
        self.status_code = Codes.INVALID_CONSTRAINT_ERROR
