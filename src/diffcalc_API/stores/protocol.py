from typing import Any, Dict, Optional, Protocol, Union

from diffcalc.hkl.calc import HklCalculation


class HklCalcStore(Protocol):
    """
    Protocol, or interface, for interacting with the Hkl object.
    """

    responses: Dict[Union[int, str], Dict[str, Any]]

    async def create(self, name: str, collection: Optional[str]) -> None:
        ...

    async def delete(self, name: str, collection: Optional[str]) -> None:
        ...

    async def save(
        self, name: str, calc: HklCalculation, collection: Optional[str]
    ) -> None:
        ...

    async def load(self, name: str, collection: Optional[str]) -> HklCalculation:
        ...
