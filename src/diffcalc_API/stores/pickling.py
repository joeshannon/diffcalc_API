"""Defines interactions with a file system persistence layer."""

import pickle
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation

from diffcalc_API.config import SAVE_PICKLES_FOLDER
from diffcalc_API.errors.definitions import (
    ALL_RESPONSES,
    DiffcalcAPIException,
    ErrorCodesBase,
)
from diffcalc_API.stores.protocol import HklType


class ErrorCodes(ErrorCodesBase):
    """Codes which can be raised in the retrieval/storage of HklCalculation objects."""

    OVERWRITE_ERROR = 405
    FILE_NOT_FOUND_ERROR = 404


class OverwriteError(DiffcalcAPIException):
    """Thrown if a HklCalculation object is created with a non-unique name."""

    def __init__(self, name):
        """Set detail and status code."""
        self.detail = (
            f"File already exists for crystal {name}!"
            f"\nEither delete via DELETE request to this URL "
            f"or change the existing properties. "
        )
        self.status_code = ErrorCodes.OVERWRITE_ERROR


class FileNotFoundError(DiffcalcAPIException):
    """Thrown if the store cannot retrieve a HklCalculation object."""

    def __init__(self, name):
        """Set detail and status code."""
        self.detail = (
            f"File for crystal {name} not found."
            f"\nYou need to post to"
            f" http://localhost:8000/{name}"
            f" first to generate the pickled file.\n"
        )
        self.status_code = ErrorCodes.FILE_NOT_FOUND_ERROR


class PicklingHklCalcStore:
    """Class to use the file system as a persistence layer for the API."""

    _root_directory: Path = Path(SAVE_PICKLES_FOLDER)

    def __init__(self) -> None:
        """Set error codes that could be thrown during method excecution.

        Purely for documentation purposes.
        """
        self.responses = {
            code: ALL_RESPONSES[code] for code in np.unique(ErrorCodes.all_codes())
        }

    async def get_all(self, name: str) -> Dict[str, List[HklType]]:
        """Get all HklCalculation objects that are persisted."""
        ...

    async def get_all_within_collection(self, collection: str) -> List[HklType]:
        """Get all HklCalculation objects that are persisted within a collection."""
        ...

    async def create(self, name: str, collection: Optional[str]) -> None:
        """Create a HklCalculation object.

        Args:
            name: the unique name to attribute to the object
            collection: the collection to store it inside.
        """
        pickled_file = (
            Path(SAVE_PICKLES_FOLDER) / (collection if collection else "default") / name
        )

        if (pickled_file).is_file():
            raise OverwriteError(name)

        if not (pickled_file.parent).is_dir():
            pickled_file.parent.mkdir()

        ubcalc = UBCalculation(name=name)
        constraints = Constraints()
        hkl = HklCalculation(ubcalc, constraints)

        await self.save(name, hkl, collection)

    async def delete(self, name: str, collection: Optional[str]) -> None:
        """Delete a HklCalculation object.

        Args:
            name: the name by which to retrieve the object
            collection: the collection inside which it is stored.
        """
        pickled_file = (
            Path(SAVE_PICKLES_FOLDER) / (collection if collection else "default") / name
        )
        if not pickled_file.is_file():
            raise FileNotFoundError(name)

        Path(pickled_file).unlink()

    async def save(
        self, name: str, calc: HklCalculation, collection: Optional[str]
    ) -> None:
        """Update a HklCalculation object.

        Args:
            name: the name by which to retrieve the object
            collection: the collection inside which it is stored.
        """
        file_path = (
            self._root_directory / (collection if collection else "default") / name
        )
        with open(file_path, "wb") as stream:
            pickle.dump(obj=calc, file=stream)

    async def load(self, name: str, collection: Optional[str]) -> HklCalculation:
        """Load a HklCalculation object.

        Args:
            name: the name by which to retrieve the object
            collection: the collection inside which it is stored.

        Returns:
            The HklCalculation object.
        """
        file_path = (
            self._root_directory / (collection if collection else "default") / name
        )
        if not file_path.is_file():
            raise FileNotFoundError(name)

        with open(file_path, "rb") as stream:
            hkl: HklCalculation = pickle.load(stream)

        return hkl
