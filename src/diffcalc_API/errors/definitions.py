from enum import IntEnum
from typing import Any, Dict, List, Union

from pydantic import BaseModel

#######################################################################################
#                                  Class definitions                                  #
#######################################################################################


class DiffcalcAPIException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class DiffcalcExceptionModel(BaseModel):
    status_code: int
    detail: str


class ErrorCodesBase(IntEnum):
    @classmethod
    def all_codes(cls) -> List[int]:
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
