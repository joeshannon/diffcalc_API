"""Defines all errors that can be raised when accessing ub endpoints."""

from typing import Optional, Union

import numpy as np

from diffcalc_api.errors.definitions import (
    ALL_RESPONSES,
    DiffcalcAPIException,
    ErrorCodesBase,
)


class ErrorCodes(ErrorCodesBase):
    """All error codes which ub routes can raise."""

    INVALID_SET_LATTICE_PARAMS = 400
    REFERENCE_RETRIEVAL_ERROR = 403
    NO_TAG_OR_IDX_PROVIDED = 400
    BOTH_TAG_OR_IDX_PROVIDED = 400
    NO_UB_MATRIX_ERROR = 400
    NO_CRYSTAL_ERROR = 400
    INVALID_INDEX_ERROR = 400


responses = {code: ALL_RESPONSES[code] for code in np.unique(ErrorCodes.all_codes())}


class NoTagOrIdxProvidedError(DiffcalcAPIException):
    """Error that gets thrown when neither a tag or index are provided.

    Some ub routes require editing existing objects handled by a tag or index. If
    neither of these are provided, the API doesn't know which object to modify.
    """

    def __init__(self):
        """Set detail and status code."""
        self.detail = (
            "One of the following must be provided as a query parameter:"
            + " tag (string), index (integer)"
        )
        self.status_code = ErrorCodes.NO_TAG_OR_IDX_PROVIDED


class BothTagAndIdxProvidedError(DiffcalcAPIException):
    """Error that gets thrown when both a tag and index are provided.

    Some ub routes require editing existing objects handled by a tag or index. If
    both of these are provided, the API doesn't know which to choose to modify.
    """

    def __init__(self):
        """Set detail and status code."""
        self.detail = (
            "both the tag and index have been provided. These are identifiers"
            + " for a specific orientation or reflection, and so both cannot be"
            + " used. Retry with just one tag or index query parameter."
        )
        self.status_code = ErrorCodes.BOTH_TAG_OR_IDX_PROVIDED


class InvalidSetLatticeParamsError(DiffcalcAPIException):
    """Error that gets thrown if the request body is empty.

    All parameters in the request body to the endpoint which sets the lattice are
    completely optional by definition. However in practise at least some parameters
    should be provided.
    """

    def __init__(self):
        """Set detail and status code."""
        self.detail = ("please provide lattice parameters in request body",)
        self.status_code = ErrorCodes.INVALID_SET_LATTICE_PARAMS


class ReferenceRetrievalError(DiffcalcAPIException):
    """Error that gets thrown if a reflection or orientation cannot be retrieved.

    Commonly caused by an issue with the tag or index provided.
    """

    def __init__(self, handle: Optional[Union[str, int]], reference_type: str) -> None:
        """Set detail and status code."""
        self.detail = f"cannot retrieve {reference_type} with tag or index {handle}"
        self.status_code = ErrorCodes.REFERENCE_RETRIEVAL_ERROR


class NoUbMatrixError(DiffcalcAPIException):
    """When there is no U/UB matrix, some commands in diffcalc-core fail."""

    def __init__(self, message: Optional[str] = None):
        """Set detail and status code."""
        self.detail = (
            (
                "It seems like there is no UB matrix for this record. Please "
                + "try again after setting the UB matrix, either by calculating the UB"
                + " from existing reflections/orientations or setting it explicitly."
            )
            if message is None
            else message
        )
        self.status_code = ErrorCodes.NO_UB_MATRIX_ERROR


class NoCrystalError(DiffcalcAPIException):
    """When there is no crystal lattice set, some commands in diffcalc-core fail."""

    def __init__(self, message: Optional[str] = None):
        """Set detail and status code."""
        self.detail = (
            (
                "It seems like there is no crystal lattice set for this record. Please"
                + " try again after setting the lattice."
            )
            if message is None
            else message
        )
        self.status_code = ErrorCodes.NO_UB_MATRIX_ERROR


class InvalidIndexError(DiffcalcAPIException):
    """Error gets thrown if an invalid miller index name is given."""

    def __init__(self, index: str):
        """Set detail and status code."""
        self.detail = (
            "Index supplied must be one of {h, k, l}. " + f"Found {index} instead."
        )

        self.status_code = ErrorCodes.INVALID_INDEX_ERROR
