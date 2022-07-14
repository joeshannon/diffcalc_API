import pickle
from abc import ABC, abstractmethod
from pathlib import Path

from diffcalc.hkl.calc import HklCalculation

from diffcalc_API.errorDefinitions import check_file_exists


class HklCalculationRepository(ABC):
    """
    Abstract representation of a persistence layer, can have many implementations
    e.g. pickled file store, database
    """

    @abstractmethod
    async def save(self, name: str, calc: HklCalculation) -> None:
        """
        Persist a calculation, identifiable by name

        Args:
            name (str): Name of the calculation, used to find later
            calc (HklCalculation): Calculation object to persist
        """

        ...

    @abstractmethod
    async def load(self, name: str) -> HklCalculation:
        """
        Load a calculation given its name

        Args:
            name (str): Name of the calculation

        Returns:
            HklCalculation: The calculation

        Raises:
            DiffcalcAPIException: If the calculation cannot be found
        """

        ...


class PicklingHklCalculationRepository(HklCalculationRepository):
    """
    Repository implementation that used pickled objects in files
    """

    _root_directory: Path

    def __init__(self, root_directory: Path) -> None:
        self._root_directory = root_directory

    async def save(self, name: str, calc: HklCalculation) -> None:
        file_path = self._root_directory / name
        with open(file_path, "wb") as stream:
            pickle.dump(obj=object, file=stream)

    async def load(self, name: str) -> HklCalculation:
        file_path = self._root_directory / name
        check_file_exists(file_path, name)

        with open(file_path, "rb") as stream:
            diffcalcObject: HklCalculation = pickle.load(stream)

        return diffcalcObject
