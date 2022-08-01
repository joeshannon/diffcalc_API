import numpy as np

from diffcalc_API.errors.definitions import (
    ALL_RESPONSES,
    DiffcalcAPIException,
    ErrorCodes,
)


class Codes(ErrorCodes):
    INVALID_MILLER_INDICES_ERROR = 400
    INVALID_SCAN_BOUNDS_ERROR = 400


responses = {code: ALL_RESPONSES[code] for code in np.unique(Codes.all_codes())}


class InvalidMillerIndicesError(DiffcalcAPIException):
    def __init__(self) -> None:
        self.detail = "At least one of the hkl indices must be non-zero"
        self.status_code = Codes.INVALID_MILLER_INDICES_ERROR


class InvalidScanBoundsError(DiffcalcAPIException):
    def __init__(self, start: float, stop: float, inc: float) -> None:
        self.detail = (
            f"numpy range cannot be formed from start: {start}"
            f" to stop: {stop} in increments of: {inc}"
        )
        self.status_code = Codes.INVALID_SCAN_BOUNDS_ERROR
