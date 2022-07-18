from typing import Any, Dict, Union

from diffcalc.util import DiffcalcException
from pydantic import BaseModel

#######################################################################################
#                                  Class definitions                                  #
#######################################################################################


class DiffcalcAPIException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class DiffcalcCoreException(DiffcalcException):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class DiffcalcExceptionModel(BaseModel):
    status_code: int
    detail: str


class ErrorCodes:
    def all_codes(self):
        attributes = [
            attr
            for attr in dir(self)
            if (not attr.startswith("__")) and (not attr == "all_codes")
        ]
        return [getattr(self, attr) for attr in attributes]


#######################################################################################
#                             All possible error responses                            #
#######################################################################################


all_responses: Dict[Union[int, str], Dict[str, Any]] = {
    400: {"model": DiffcalcExceptionModel, "description": "Bad Request"},
    403: {"model": DiffcalcExceptionModel, "description": "Forbidden Request"},
    404: {"model": DiffcalcExceptionModel, "description": "Resource Not Found"},
    405: {"model": DiffcalcExceptionModel, "description": "Request disabled"},
    500: {"model": DiffcalcExceptionModel, "description": "Internal Server Error"},
}
