from typing import Any, Dict, Optional

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation
from motor.motor_asyncio import AsyncIOMotorCollection as Collection
from pymongo.results import DeleteResult

from diffcalc_API.database import database
from diffcalc_API.errors.definitions import (
    ALL_RESPONSES,
    DiffcalcAPIException,
    ErrorCodes,
)
from diffcalc_API.stores.protocol import HklCalcStore


class Codes(ErrorCodes):
    attempting_to_overwrite = 405
    document_found = 404
    nothing_to_delete = 404


def attempting_to_overwrite(name: str, collection: Collection) -> None:
    existing_document = collection.find_one({"ubcalc.name": name})
    if existing_document:
        message = (
            f"Document already exists for crystal {name}!"
            f"\nEither delete via DELETE request to this URL "
            f"or change the existing properties. "
        )
        raise DiffcalcAPIException(
            status_code=Codes.attempting_to_overwrite, detail=message
        )


def document_found(name: str, retrieved_document: Optional[Dict[str, Any]]):
    if not retrieved_document:
        message = f"Document for crystal {name} not found! Cannot load."
        raise DiffcalcAPIException(status_code=Codes.document_found, detail=message)


def nothing_to_delete(name: str, result: DeleteResult):
    if result.deleted_count == 0:
        message = f"Document for crystal {name} not found! Cannot delete"
        raise DiffcalcAPIException(status_code=Codes.nothing_to_delete, detail=message)


class MongoHklCalcStore:
    def __init__(
        self,
    ) -> None:  # in future, you can use init to make this beamline specific.
        self.responses = {
            code: ALL_RESPONSES[code] for code in np.unique(Codes().all_codes())
        }

    async def create(self, name: str, collection: Optional[str]) -> None:
        coll: Collection = database[collection if collection else "default"]

        attempting_to_overwrite(name, coll)
        ubcalc = UBCalculation(name=name)
        constraints = Constraints()
        hkl = HklCalculation(ubcalc, constraints)

        await coll.insert_one(hkl.asdict)

    async def delete(self, name: str, collection: Optional[str]) -> None:
        coll: Collection = database[collection if collection else "default"]
        result: DeleteResult = await coll.delete_one({"ubcalc.name": name})
        nothing_to_delete(name, result)

    async def save(
        self, name: str, hkl: HklCalculation, collection: Optional[str]
    ) -> None:
        coll: Collection = database[collection if collection else "default"]
        await coll.find_one_and_update({"ubcalc.name": name}, {"$set": hkl.asdict})

    async def load(self, name: str, collection: Optional[str]) -> HklCalculation:
        coll: Collection = database[collection if collection else "default"]
        hkl_json: Optional[Dict[str, Any]] = await coll.find_one({"ubcalc.name": name})
        document_found(name, hkl_json)
        return HklCalculation.fromdict(hkl_json)


def get_store() -> HklCalcStore:
    return MongoHklCalcStore()
