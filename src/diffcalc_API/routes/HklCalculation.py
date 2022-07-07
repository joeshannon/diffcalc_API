from typing import Tuple, Union

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.geometry import Position
from fastapi import APIRouter, Body, Depends

from diffcalc_API.models.HklCalculation import (
    labPosFromMillerParams,
    millerPosFromLabParams,
)
from diffcalc_API.utils import unpickleHkl

router = APIRouter(prefix="/calculate", tags=["hkl"])


# Collection is not supported, so I explicitly define it here.
singleConstraintType = Union[Tuple[str, float], str]


@router.post("/{name}/lab/position")
async def get_lab_positions_from_set_of_miller_indices(
    name: str,
    params: labPosFromMillerParams = Body(
        example={"indices": [0, 0, 1], "wavelength": 1.0}
    ),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    if isinstance(params.indices, tuple):
        position = lab_position_from_hkl(hkl, params.indices, params.wavelength)
        return {"payload": position}

    positions = [
        lab_position_from_hkl(hkl, indices, params.wavelength)
        for indices in params.indices
    ]

    return {"payload": positions}


def lab_position_from_hkl(
    hkl: HklCalculation, millerIndices: Tuple[float, float, float], wavelength: float
):
    allPositions = hkl.get_position(*millerIndices, wavelength)

    for position in allPositions:
        if validate_lab_position(position[0]):
            break

    return position[0].asdict


def validate_lab_position(pos: Position):
    return all((0 < pos.mu < 90, 0 < pos.nu < 90, -90 < pos.phi < 90))


@router.post("/{name}/hkl/position")
async def get_miller_indices_from_lab_position(
    name: str,
    params: millerPosFromLabParams = Body(
        example={"labPosition": [7.31, 0, 10.62, 0, 0, 0], "wavelength": 1.0}
    ),
    hkl: HklCalculation = Depends(unpickleHkl),
):
    hklPosition = hkl.get_hkl(Position(*params.labPosition), params.wavelength)
    return {"payload": tuple(np.round(hklPosition, 16))}


"""
def check_iterable(millerIndices: Union[Iterable[positionType], positionType]):
    print("done")


if __name__ == "__main__":
    check_iterable((1, 2, 3))
    print("success")
    check_iterable([(1, 0, 0), (0, 1, 1)])
"""
