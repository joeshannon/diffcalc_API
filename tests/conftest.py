from diffcalc.hkl.calc import HklCalculation

from diffcalc_API.fileHandling import HklCalcRepo


class FakeHklCalcRepo(HklCalcRepo):
    def __init__(self, useHkl: HklCalculation):
        self.hkl = useHkl

    async def save(self, name: str, calc: HklCalculation) -> None:
        return

    async def load(self, name: str) -> HklCalculation:
        return self.hkl
