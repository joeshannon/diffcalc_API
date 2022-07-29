from typing import Any, Dict, Optional, Union

from diffcalc.hkl.calc import HklCalculation


class FakeHklCalcStore:
    def __init__(self, hkl: HklCalculation):
        self.hkl = hkl
        self.responses: Dict[Union[int, str], Dict[str, Any]] = {}

    async def create(self, name: str, collection: Optional[str]) -> None:
        pass

    async def delete(self, name: str, collection: Optional[str]) -> None:
        pass

    async def save(
        self, name: str, calc: HklCalculation, collection: Optional[str]
    ) -> None:
        pass

    async def load(self, name: str, collection: Optional[str]) -> HklCalculation:
        return self.hkl

    def use_hkl(self, hkl: HklCalculation):
        self.hkl = hkl
