"""Errors that can be raised when accessing /hkl/ endpoints."""
from typing import Optional

import numpy as np

from diffcalc_api.errors.definitions import (
    ALL_RESPONSES,
    DiffcalcAPIException,
    ErrorCodesBase,
)


class ErrorCodes(ErrorCodesBase):
    """All error codes which hkl routes can raise."""

    INVALID_MILLER_INDICES = 400
    INVALID_SCAN_BOUNDS = 400
    INVALID_SOLUTION_BOUNDS = 400


responses = {code: ALL_RESPONSES[code] for code in np.unique(ErrorCodes.all_codes())}


class InvalidMillerIndicesError(DiffcalcAPIException):
    """Error that gets thrown when provided miller indices are invalid."""

    def __init__(self, detail: Optional[str] = None) -> None:
        """Set detail and status code."""
        self.detail = (
            "At least one of the hkl indices must be non-zero" if not detail else detail
        )
        self.status_code = ErrorCodes.INVALID_MILLER_INDICES


class InvalidScanBoundsError(DiffcalcAPIException):
    """Error that gets thrown when provided scan bounds are invalid."""

    def __init__(self, start: float, stop: float, inc: float) -> None:
        """Set detail and status code."""
        self.detail = (
            f"numpy range cannot be formed from start: {start}"
            f" to stop: {stop} in increments of: {inc}"
        )
        self.status_code = ErrorCodes.INVALID_SCAN_BOUNDS


class InvalidSolutionBoundsError(DiffcalcAPIException):
    """Error that gets thrown when provided solution bounds are invalid.

    The diffraction angle calculator often provides multiple diffractometer
    angles as equivalent to a set of miller indices. Solution bounds can be provided
    to constrain these, however they must pass some checks before use.
    """

    def __init__(self, detail: str) -> None:
        """Set detail and status code."""
        self.detail = detail
        self.status_code = ErrorCodes.INVALID_SOLUTION_BOUNDS
