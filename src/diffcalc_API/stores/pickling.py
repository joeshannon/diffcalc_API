import pickle
from pathlib import Path
from typing import Optional

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation

from diffcalc_API.config import SAVE_PICKLES_FOLDER
from diffcalc_API.errors.definitions import (
    ALL_RESPONSES,
    DiffcalcAPIException,
    ErrorCodes,
)
from diffcalc_API.stores.protocol import HklCalcStore


class Codes(ErrorCodes):
    attempting_to_overwrite = 405
    check_file_exists = 404


def attempting_to_overwrite(filename: str) -> None:
    pickled_file = Path(SAVE_PICKLES_FOLDER) / filename
    if (pickled_file).is_file():
        message = (
            f"File already exists for crystal {filename}!"
            f"\nEither delete via DELETE request to this URL "
            f"or change the existing properties. "
        )
        raise DiffcalcAPIException(
            status_code=Codes.attempting_to_overwrite, detail=message
        )


def check_file_exists(pickled_file: Path, name: str) -> None:
    if not (pickled_file).is_file():
        message = (
            f"File for crystal {name} not found."
            f"\nYou need to post to"
            f" http://localhost:8000/{name}"
            f" first to generate the pickled file.\n"
        )
        raise DiffcalcAPIException(status_code=Codes.check_file_exists, detail=message)


class PicklingHklCalcStore:
    _root_directory: Path

    def __init__(self, root_directory: Path) -> None:
        self._root_directory = root_directory
        self.responses = {
            code: ALL_RESPONSES[code] for code in np.unique(Codes().all_codes())
        }

    async def create(self, name: str, collection: Optional[str]) -> None:
        attempting_to_overwrite(name)

        ubcalc = UBCalculation(name=name)
        constraints = Constraints()
        hkl = HklCalculation(ubcalc, constraints)

        await self.save(name, hkl, collection)

    async def delete(self, name: str, collection: Optional[str]) -> None:
        pickle_file_path = (
            Path(SAVE_PICKLES_FOLDER) / (collection if collection else "default") / name
        )
        check_file_exists(pickle_file_path, name)
        Path(pickle_file_path).unlink()

    async def save(
        self, name: str, calc: HklCalculation, collection: Optional[str]
    ) -> None:
        file_path = (
            self._root_directory / (collection if collection else "default") / name
        )
        with open(file_path, "wb") as stream:
            pickle.dump(obj=calc, file=stream)

    async def load(self, name: str, collection: Optional[str]) -> HklCalculation:
        file_path = (
            self._root_directory / (collection if collection else "default") / name
        )
        check_file_exists(file_path, name)

        with open(file_path, "rb") as stream:
            hkl: HklCalculation = pickle.load(stream)

        return hkl


def get_store() -> HklCalcStore:
    return PicklingHklCalcStore(Path(SAVE_PICKLES_FOLDER))
