import pickle
from abc import ABC, abstractmethod
from pathlib import Path

from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation

from diffcalc_API.config import savePicklesFolder
from diffcalc_API.errorDefinitions import attempting_to_overwrite, check_file_exists


class HklCalcRepo(ABC):
    """
    Abstract representation of persistence, can have various implementations to edit
    the state which the API is managing (hkl object).
    """

    @abstractmethod
    async def save(self, name: str, calc: HklCalculation) -> None:
        ...

    @abstractmethod
    async def load(self, name: str) -> HklCalculation:
        ...


class PicklingHklCalcRepo(HklCalcRepo):
    _root_directory: Path

    def __init__(self, root_directory: Path) -> None:
        self._root_directory = root_directory

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


def get_repo() -> HklCalcRepo:
    return PicklingHklCalcRepo(Path(savePicklesFolder))


def createPickle(pickleFileName: str) -> Path:
    attempting_to_overwrite(pickleFileName)

    UBcalc = UBCalculation(name=pickleFileName)
    constraints = Constraints()
    hkl = HklCalculation(UBcalc, constraints)

    repo = get_repo()
    repo.save(pickleFileName, hkl)

    return Path(savePicklesFolder, pickleFileName)


def deletePickle(pickleFileName: str) -> Path:
    pickleFilePath = Path(savePicklesFolder) / pickleFileName
    check_file_exists(pickleFilePath, pickleFileName)
    Path(pickleFilePath).unlink()

    return pickleFilePath
