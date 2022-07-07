from typing import Tuple, Union

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.geometry import Position
from fastapi import APIRouter, Depends, HTTPException, Query

from diffcalc_API.utils import unpickleHkl

router = APIRouter(prefix="/calculate", tags=["hkl"])


# Collection is not supported, so I explicitly define it here.
singleConstraintType = Union[Tuple[str, float], str]


@router.get("/{name}/lab/position")
async def lab_position_from_miller_indices(
    name: str,
    pos: Tuple[float, float, float] = Query(example=[0, 0, 1]),
    wavelength: float = Query(..., example=1.0),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    if sum(pos) == 0:
        raise HTTPException(
            status_code=401, detail="At least one of the hkl indices must be non-zero"
        )

    allPositions = hkl.get_position(*pos, wavelength)

    for position in allPositions:
        if validate_lab_position(position[0]):
            break

    return {"payload": position[0].asdict}


def validate_lab_position(pos: Position):
    return all((0 < pos.mu < 90, 0 < pos.nu < 90, -90 < pos.phi < 90))


@router.get("/{name}/hkl/position")
async def miller_indices_from_lab_position(
    name: str,
    pos: Tuple[float, float, float, float, float, float] = Query(
        default=[0, 0, 0, 0, 0, 0], example=[7.31, 0, 10.62, 0, 0, 0]
    ),
    wavelength: float = Query(..., example=1.0),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    hklPosition = hkl.get_hkl(Position(*pos), wavelength)
    return {"payload": tuple(np.round(hklPosition, 16))}
