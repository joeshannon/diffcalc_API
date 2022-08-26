"""Errors used throughout the package and for documentation."""

from enum import IntEnum
from typing import Any, Dict, List, Union

from pydantic import BaseModel

#######################################################################################
#                                  Class definitions                                  #
#######################################################################################


class DiffcalcAPIException(Exception):
    """Error when there is an issue with the request."""

    def __init__(self, status_code: int, detail: str):
        """Set status code and detail."""
        self.status_code = status_code
        self.detail = detail


class DiffcalcExceptionModel(BaseModel):
    """Error when there is an issue with diffcalc-core's execution of the request."""

    status_code: int
    detail: str


class ErrorCodesBase(IntEnum):
    """Base class to store multiple error codes for documentation/testing purposes."""

    @classmethod
    def all_codes(cls) -> List[int]:
        """Generate a list of all the code values for documentation purposes."""
        return [val.value for val in cls]


#######################################################################################
#                             All possible error responses                            #
#######################################################################################


ALL_RESPONSES: Dict[Union[int, str], Dict[str, Any]] = {
    400: {"model": DiffcalcExceptionModel, "description": "Bad Request"},
    403: {"model": DiffcalcExceptionModel, "description": "Forbidden Request"},
    404: {"model": DiffcalcExceptionModel, "description": "Resource Not Found"},
    405: {"model": DiffcalcExceptionModel, "description": "Request disabled"},
    500: {"model": DiffcalcExceptionModel, "description": "Internal Server Error"},
}
