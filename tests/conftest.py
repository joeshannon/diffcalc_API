from typing import Any, Dict, List, Optional, Union

from diffcalc.hkl.calc import HklCalculation

from diffcalc_API.useful_types import HklType


class FakeHklCalcStore:
    def __init__(self, hkl: HklCalculation):
        self.hkl = hkl
        self.responses: Dict[Union[int, str], Dict[str, Any]] = {}

    async def get_all(self, name: str) -> Dict[str, List[HklType]]:
        """Get all HklCalculation objects that are persisted."""
        ...

    async def get_all_within_collection(self, collection: str) -> List[HklType]:
        """Get all HklCalculation objects that are persisted within a collection."""
        ...

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
