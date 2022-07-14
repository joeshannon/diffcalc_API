from typing import Tuple, Union

from diffcalc.hkl.geometry import Position

from diffcalc_API.errors.UBCalculation import get_orientation, get_reflection
from diffcalc_API.fileHandling import HklCalcRepo
from diffcalc_API.models.UBCalculation import (
    addOrientationParams,
    addReflectionParams,
    editOrientationParams,
    editReflectionParams,
    setLatticeParams,
)


async def get_UB(name: str, repo: HklCalcRepo) -> str:
    hklCalc = await repo.load(name)

    return str(hklCalc.ubcalc)


async def add_reflection(
    name: str,
    params: addReflectionParams,
    repo: HklCalcRepo,
) -> None:
    hklCalc = await repo.load(name)

    hklCalc.ubcalc.add_reflection(
        params.hkl,
        Position(*params.position),
        params.energy,
        params.tag,
    )

    repo.save(name, hklCalc)


async def edit_reflection(
    name: str,
    params: editReflectionParams,
    repo: HklCalcRepo,
) -> None:
    hklCalc = await repo.load(name)

    reflection = get_reflection(hklCalc, params.tagOrIdx)
    hklCalc.ubcalc.edit_reflection(
        params.tagOrIdx,
        params.hkl if params.hkl else (reflection.h, reflection.k, reflection.l),
        Position(params.position) if params.position else reflection.pos,
        params.energy if params.energy else reflection.energy,
        params.tagOrIdx if isinstance(params.tagOrIdx, str) else None,
    )

    repo.save(name, hklCalc)


async def delete_reflection(
    name: str,
    tagOrIdx: Union[str, int],
    repo: HklCalcRepo,
) -> None:
    hklCalc = await repo.load(name)

    _ = get_reflection(hklCalc, tagOrIdx)
    hklCalc.ubcalc.del_reflection(tagOrIdx)

    repo.save(name, hklCalc)


async def add_orientation(
    name: str,
    params: addOrientationParams,
    repo: HklCalcRepo,
) -> None:
    hklCalc = await repo.load(name)

    position = Position(*params.position) if params.position else None
    hklCalc.ubcalc.add_orientation(
        params.hkl,
        params.xyz,
        position,
        params.tag,
    )

    repo.save(name, hklCalc)


async def edit_orientation(
    name: str,
    params: editOrientationParams,
    repo: HklCalcRepo,
) -> None:
    hklCalc = await repo.load(name)

    orientation = get_orientation(hklCalc, params.tagOrIdx)
    hklCalc.ubcalc.edit_orientation(
        params.tagOrIdx,
        params.hkl if params.hkl else (orientation.h, orientation.k, orientation.l),
        params.xyz if params.xyz else (orientation.x, orientation.y, orientation.z),
        Position(params.position) if params.position else orientation.pos,
        params.tagOrIdx if isinstance(params.tagOrIdx, str) else None,
    )

    repo.save(name, hklCalc)


async def delete_orientation(
    name: str,
    tagOrIdx: Union[str, int],
    repo: HklCalcRepo,
) -> None:
    hklCalc = await repo.load(name)

    _ = get_orientation(hklCalc, tagOrIdx)
    hklCalc.ubcalc.del_orientation(tagOrIdx)

    repo.save(name, hklCalc)


async def set_lattice(name: str, params: setLatticeParams, repo: HklCalcRepo) -> None:
    hklCalc = await repo.load(name)

    hklCalc.ubcalc.set_lattice(name=name, **params.dict())

    repo.save(name, hklCalc)


async def modify_property(
    name: str, property: str, targetValue: Tuple[float, float, float], repo: HklCalcRepo
):
    hklCalc = await repo.load(name)

    setattr(hklCalc.ubcalc, property, targetValue)

    repo.save(name, hklCalc)
