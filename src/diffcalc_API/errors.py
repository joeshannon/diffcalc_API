from typing import Any, Dict, Optional, Union

from diffcalc.util import DiffcalcException
from pydantic import BaseModel


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


responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = {
    404: {"model": DiffcalcExceptionModel, "description": "Resource not found"},
    405: {"model": DiffcalcExceptionModel, "description": "Request disabled"},
}
