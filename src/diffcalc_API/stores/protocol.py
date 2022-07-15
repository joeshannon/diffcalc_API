from typing import Protocol

from diffcalc.hkl.calc import HklCalculation


class HklCalcStore(Protocol):
    """
    Protocol, or interface, for interacting with the Hkl object.
    """

    async def create(self, name: str) -> None:
        ...

    async def delete(self, name: str) -> None:
        ...

    async def save(self, name: str, calc: HklCalculation) -> None:
        ...

    async def load(self, name: str) -> HklCalculation:
        ...
