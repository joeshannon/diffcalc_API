from pathlib import Path
from typing import Callable, Optional, Tuple, Union

from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.geometry import Position

from diffcalc_API.errors.UBCalculation import (
    calculate_UB_matrix,
    get_orientation,
    get_reflection,
)
from diffcalc_API.models.UBCalculation import (
    addOrientationParams,
    addReflectionParams,
    editOrientationParams,
    editReflectionParams,
    setLatticeParams,
)


def add_reflection(
    name: str,
    params: addReflectionParams,
    hklCalc: HklCalculation,
    persist: Callable[[HklCalculation, str], Path],
):
    hklCalc.ubcalc.add_reflection(
        params.hkl,
        Position(*params.position),
        params.energy,
        params.tag,
    )

    persist(hklCalc, name)
    return


def edit_reflection(
    name: str,
    params: editReflectionParams,
    hklCalc: HklCalculation,
    persist: Callable[[HklCalculation, str], Path],
):
    reflection = get_reflection(hklCalc, params.tagOrIdx)

    hklCalc.ubcalc.edit_reflection(
        params.tagOrIdx,
        params.hkl if params.hkl else (reflection.h, reflection.k, reflection.l),
        Position(params.position) if params.position else reflection.pos,
        params.energy if params.energy else reflection.energy,
        params.tagOrIdx if isinstance(params.tagOrIdx, str) else None,
    )
    persist(hklCalc, name)
    return


def delete_reflection(
    name: str,
    tagOrIdx: Union[str, int],
    hklCalc: HklCalculation,
    persist: Callable[[HklCalculation, str], Path],
):
    _ = get_reflection(hklCalc, tagOrIdx)
    hklCalc.ubcalc.del_reflection(tagOrIdx)
    persist(hklCalc, name)
    return


def add_orientation(
    name: str,
    params: addOrientationParams,
    hklCalc: HklCalculation,
    persist: Callable[[HklCalculation, str], Path],
):
    position = Position(*params.position) if params.position else None

    hklCalc.ubcalc.add_orientation(
        params.hkl,
        params.xyz,
        position,
        params.tag,
    )

    persist(hklCalc, name)
    return


def edit_orientation(
    name: str,
    params: editOrientationParams,
    hklCalc: HklCalculation,
    persist: Callable[[HklCalculation, str], Path],
):
    orientation = get_orientation(hklCalc, params.tagOrIdx)

    hklCalc.ubcalc.edit_orientation(
        params.tagOrIdx,
        params.hkl if params.hkl else (orientation.h, orientation.k, orientation.l),
        params.xyz if params.xyz else (orientation.x, orientation.y, orientation.z),
        Position(params.position) if params.position else orientation.pos,
        params.tagOrIdx if isinstance(params.tagOrIdx, str) else None,
    )
    persist(hklCalc, name)
    return


def delete_orientation(
    name: str,
    tagOrIdx: Union[str, int],
    hklCalc: HklCalculation,
    persist: Callable[[HklCalculation, str], Path],
):
    _ = get_orientation(hklCalc, tagOrIdx)
    hklCalc.ubcalc.del_orientation(tagOrIdx)
    persist(hklCalc, name)


def set_lattice(
    name: str,
    params: setLatticeParams,
    hklCalc: HklCalculation,
    persist: Callable[[HklCalculation, str], Path],
):
    hklCalc.ubcalc.set_lattice(name=name, **params.dict())
    persist(hklCalc, name)


def modify_property(
    name: str,
    property: str,
    targetValue: Tuple[float, float, float],
    hklCalc: HklCalculation,
    persist: Callable[[HklCalculation, str], Path],
):
    setattr(hklCalc.ubcalc, property, targetValue)
    persist(hklCalc, name)


def calculate_UB(
    name: str,
    firstTag: Optional[Union[int, str]],
    secondTag: Optional[Union[int, str]],
    hklCalc: HklCalculation,
    persist: Callable[[HklCalculation, str], Path],
):
    calculate_UB_matrix(hklCalc, firstTag, secondTag)
    persist(hklCalc, name)
