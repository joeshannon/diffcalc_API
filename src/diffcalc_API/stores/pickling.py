import pickle
from pathlib import Path

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation

from diffcalc_API.config import savePicklesFolder
from diffcalc_API.errors.definitions import (
    DiffcalcAPIException,
    ErrorCodes,
    allResponses,
)
from diffcalc_API.stores.protocol import HklCalcStore


class Codes(ErrorCodes):
    attempting_to_overwrite = 405
    check_file_exists = 404


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


class PicklingHklCalcStore:
    _root_directory: Path

    def __init__(self, root_directory: Path) -> None:
        self._root_directory = root_directory
        self.responses = {
            code: allResponses[code] for code in np.unique(Codes().all_codes())
        }

    async def create(self, name: str) -> None:
        attempting_to_overwrite(name)

        UBcalc = UBCalculation(name=name)
        constraints = Constraints()
        hkl = HklCalculation(UBcalc, constraints)

        await self.save(name, hkl)

    async def delete(self, name: str) -> None:
        pickleFilePath = Path(savePicklesFolder) / name
        check_file_exists(pickleFilePath, name)
        Path(pickleFilePath).unlink()

    async def save(self, name: str, calc: HklCalculation) -> None:
        file_path = self._root_directory / name
        with open(file_path, "wb") as stream:
            pickle.dump(obj=calc, file=stream)

    async def load(self, name: str) -> HklCalculation:
        file_path = self._root_directory / name
        check_file_exists(file_path, name)

        with open(file_path, "rb") as openedFile:
            diffcalcObject: HklCalculation = pickle.load(openedFile)

        return diffcalcObject


def get_store() -> HklCalcStore:
    return PicklingHklCalcStore(Path(savePicklesFolder))
