from pathlib import Path
from typing import Callable, Dict, Union

from diffcalc.hkl.calc import HklCalculation
from fastapi import APIRouter, Body, Depends

from diffcalc_API.config import savePicklesFolder
from diffcalc_API.controllers import Constraints as controller
from diffcalc_API.fileHandling import supplyPersist, unpickleHkl
from diffcalc_API.persistence import (
    HklCalculationRepository,
    PicklingHklCalculationRepository,
)

router = APIRouter(prefix="/constraints", tags=["constraints"])


def get_repo() -> HklCalculationRepository:
    return PicklingHklCalculationRepository(Path(savePicklesFolder))


@router.put("/{name}/set")
async def set_constraints(
    name: str,
    constraintDict: Dict[str, Union[float, bool]] = Body(
        example={"qaz": 0, "alpha": 0, "eta": 0}
    ),
    repo: HklCalculationRepository = Depends(get_repo),
):
    # await controller.set_constraints(name, constraintDict, repo)
    return {"message": f"constraints updated (replaced) for crystal {name}"}


@router.patch("/{name}/unconstrain/{property}")
async def remove_constraint(
    name: str,
    property: str,
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    controller.remove_constraint(name, property, hklCalc, persist)

    return {
        "message": (
            f"unconstrained {property} for crystal {name}. "
            f"Constraints are now: {hklCalc.constraints.asdict}"
        )
    }


@router.patch("/{name}/constrain/{property}")
async def set_constraint(
    name: str,
    property: str,
    value: Union[float, bool] = Body(...),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    controller.set_constraint(name, property, value, hklCalc, persist)

    return {
        "message": (
            f"constrained {property} for crystal {name}. "
            f"Constraints are now: {hklCalc.constraints.asdict}"
        )
    }
