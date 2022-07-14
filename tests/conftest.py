from diffcalc.hkl.calc import HklCalculation

from diffcalc_API.persistence import HklCalcStore


class FakeHklCalcStore(HklCalcStore):
    def __init__(self, useHkl: HklCalculation):
        self.hkl = useHkl

    async def create(self, name: str) -> None:
        pass

    async def delete(self, name: str) -> None:
        pass

    async def save(self, name: str, calc: HklCalculation) -> None:
        pass

    async def load(self, name: str) -> HklCalculation:
        return self.hkl
