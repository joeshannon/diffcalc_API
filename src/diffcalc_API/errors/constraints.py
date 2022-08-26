"""Errors that can be raised when accessing constraints endpoints."""
import numpy as np

from diffcalc_API.config import ALL_CONSTRAINTS
from diffcalc_API.errors.definitions import (
    ALL_RESPONSES,
    DiffcalcAPIException,
    ErrorCodesBase,
)


class ErrorCodes(ErrorCodesBase):
    """All error codes which constraints routes can raise."""

    INVALID_CONSTRAINT = 400


responses = {code: ALL_RESPONSES[code] for code in np.unique(ErrorCodes.all_codes())}


class InvalidConstraintError(DiffcalcAPIException):
    """Error that gets thrown when the provided constraint is invalid."""

    def __init__(self, constraint: str):
        """Set detail and status code."""
        self.detail = (
            f"property {constraint} does not exist as a valid constraint."
            f" Valid constraints are: {ALL_CONSTRAINTS}"
        )
        self.status_code = ErrorCodes.INVALID_CONSTRAINT
