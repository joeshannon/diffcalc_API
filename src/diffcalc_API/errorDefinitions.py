from pathlib import Path

import numpy as np
from diffcalc.util import DiffcalcException
from pydantic import BaseModel

from diffcalc_API.config import savePicklesFolder

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
#                               Error throwing functions                              #
#######################################################################################


class codes(ErrorCodes):
    attempting_to_overwrite = 405
    check_file_exists = 404


allResponses = {
    400: {"model": DiffcalcExceptionModel, "description": "Bad Request"},
    403: {"model": DiffcalcExceptionModel, "description": "Forbidden Request"},
    404: {"model": DiffcalcExceptionModel, "description": "Resource Not Found"},
    405: {"model": DiffcalcExceptionModel, "description": "Request disabled"},
    500: {"model": DiffcalcExceptionModel, "description": "Internal Server Error"},
}

responses = {code: allResponses[code] for code in np.unique(codes().all_codes())}


def attempting_to_overwrite(fileName: str) -> None:
    pickledFile = Path(savePicklesFolder) / fileName
    if (pickledFile).is_file():
        errorMessage = (
            f"File already exists for crystal {fileName}!"
            f"\nEither delete via DELETE request to this URL "
            f"or change the existing properties. "
        )
        raise DiffcalcAPIException(status_code=405, detail=errorMessage)

    return


def check_file_exists(pickledFile: Path, name: str) -> None:
    if not (pickledFile).is_file():
        errorMessage = (
            f"File for crystal {name} not found."
            f"\nYou need to post to"
            f" http://localhost:8000/{name}"
            f" first to generate the pickled file.\n"
        )
        raise DiffcalcAPIException(status_code=404, detail=errorMessage)
