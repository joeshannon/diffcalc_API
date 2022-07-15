import pickle
from pathlib import Path

from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation

from diffcalc_API.config import savePicklesFolder
from diffcalc_API.errorDefinitions import attempting_to_overwrite, check_file_exists
from diffcalc_API.stores.protocol import HklCalcStore


class PicklingHklCalcStore:
    _root_directory: Path

    def __init__(self, root_directory: Path) -> None:
        self._root_directory = root_directory

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
