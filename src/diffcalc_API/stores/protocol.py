"""Protocol for HklCalculation persistence.

Defines how HklCalculation objects ought to be accessed in the API, and what methods
must be provided by persistence methods for API services to access them.
"""

from importlib import import_module
from typing import Any, Dict, Optional, Protocol, Union

from diffcalc.hkl.calc import HklCalculation


class HklCalcStore(Protocol):
    """Protocol for interacting with the HklCalculation object."""

    responses: Dict[Union[int, str], Dict[str, Any]]

    async def create(self, name: str, collection: Optional[str]) -> None:
        """Create a HklCalculation object."""
        ...

    async def delete(self, name: str, collection: Optional[str]) -> None:
        """Delete a HklCalculation object."""
        ...

    async def save(
        self, name: str, calc: HklCalculation, collection: Optional[str]
    ) -> None:
        """Save a HklCalculation object."""
        ...

    async def load(self, name: str, collection: Optional[str]) -> HklCalculation:
        """Load a HklCalculation object."""
        ...


STORE: Optional[HklCalcStore] = None


def get_store() -> HklCalcStore:
    """Retrieve the class which handles HklCalculation objects."""
    if STORE is None:
        raise ValueError()
    return STORE


def setup_store(store_location: str, *args) -> None:
    """Allow the server to select which store to use."""
    global STORE
    path, clsname = store_location.rsplit(".", 1)
    STORE = getattr(import_module(path), clsname)(*args)
