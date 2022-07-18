from typing import Any, Dict, Union

from diffcalc.hkl.calc import HklCalculation


class FakeHklCalcStore:
    def __init__(self, hkl: HklCalculation):
        self.hkl = hkl
        self.responses: Dict[Union[int, str], Dict[str, Any]] = {}

    async def create(self, name: str) -> None:
        pass

    async def delete(self, name: str) -> None:
        pass

    async def save(self, name: str, calc: HklCalculation) -> None:
        pass

    async def load(self, name: str) -> HklCalculation:
        return self.hkl
