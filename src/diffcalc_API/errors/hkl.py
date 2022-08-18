from typing import Optional

import numpy as np

from diffcalc_API.errors.definitions import (
    ALL_RESPONSES,
    DiffcalcAPIException,
    ErrorCodesBase,
)


class ErrorCodes(ErrorCodesBase):
    INVALID_MILLER_INDICES = 400
    INVALID_SCAN_BOUNDS = 400


responses = {code: ALL_RESPONSES[code] for code in np.unique(ErrorCodes.all_codes())}


class InvalidMillerIndicesError(DiffcalcAPIException):
    def __init__(self, detail: Optional[str] = None) -> None:
        self.detail = (
            "At least one of the hkl indices must be non-zero" if not detail else detail
        )
        self.status_code = ErrorCodes.INVALID_MILLER_INDICES


class InvalidScanBoundsError(DiffcalcAPIException):
    def __init__(self, start: float, stop: float, inc: float) -> None:
        self.detail = (
            f"numpy range cannot be formed from start: {start}"
            f" to stop: {stop} in increments of: {inc}"
        )
        self.status_code = ErrorCodes.INVALID_SCAN_BOUNDS
