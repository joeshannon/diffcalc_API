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
    ErrorCodesBase,
)


class ErrorCodes(ErrorCodesBase):
    OVERWRITE_ERROR = 405
    DOCUMENT_NOT_FOUND_ERROR = 404


class OverwriteError(DiffcalcAPIException):
    def __init__(self, name: str) -> None:
        self.detail = (
            f"Document already exists for crystal {name}!"
            f"\nEither delete via DELETE request to this URL "
            f"or change the existing properties. "
        )
        self.status_code = ErrorCodes.OVERWRITE_ERROR


class DocumentNotFoundError(DiffcalcAPIException):
    def __init__(self, name: str, action: str) -> None:
        self.detail = f"Document for crystal {name} not found! Cannot {action}."
        self.error_code = ErrorCodes.DOCUMENT_NOT_FOUND_ERROR


class MongoHklCalcStore:
    def __init__(
        self,
    ) -> None:
        self.responses = {
            code: ALL_RESPONSES[code] for code in np.unique(ErrorCodes.all_codes())
        }

    async def create(self, name: str, collection: Optional[str]) -> None:
        coll: Collection = database[collection if collection else "default"]

        if await coll.find_one({"ubcalc.name": name}):
            raise OverwriteError(name)

        ubcalc = UBCalculation(name=name)
        constraints = Constraints()
        hkl = HklCalculation(ubcalc, constraints)

        await coll.insert_one(hkl.asdict)

    async def delete(self, name: str, collection: Optional[str]) -> None:
        coll: Collection = database[collection if collection else "default"]
        result: DeleteResult = await coll.delete_one({"ubcalc.name": name})
        if result.deleted_count == 0:
            raise DocumentNotFoundError(name, "delete")

    async def save(
        self, name: str, hkl: HklCalculation, collection: Optional[str]
    ) -> None:
        coll: Collection = database[collection if collection else "default"]
        await coll.find_one_and_update({"ubcalc.name": name}, {"$set": hkl.asdict})

    async def load(self, name: str, collection: Optional[str]) -> HklCalculation:
        coll: Collection = database[collection if collection else "default"]
        hkl_json: Optional[Dict[str, Any]] = await coll.find_one({"ubcalc.name": name})
        if not hkl_json:
            raise DocumentNotFoundError(name, "load")

        return HklCalculation.fromdict(hkl_json)
