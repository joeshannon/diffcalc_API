"""Pydantic models relating to ub routes."""

from typing import Optional

from pydantic import BaseModel


class HklModel(BaseModel):
    """Model containing miller indices."""

    h: float
    k: float
    l: float


class XyzModel(BaseModel):
    """Model containing real space positions."""

    x: float
    y: float
    z: float


class PositionModel(BaseModel):
    """Model containing diffractometer angles."""

    mu: float
    delta: float
    nu: float
    eta: float
    chi: float
    phi: float


class SetLatticeParams(BaseModel):
    """Request body definition to set the lattice."""

    name: Optional[str] = None
    system: Optional[str] = None
    a: Optional[float] = None
    b: Optional[float] = None
    c: Optional[float] = None
    alpha: Optional[float] = None
    beta: Optional[float] = None
    gamma: Optional[float] = None


class AddReflectionParams(BaseModel):
    """Request body definition to add a reflection of the UB calculation."""

    hkl: HklModel
    position: PositionModel
    energy: float


class AddOrientationParams(BaseModel):
    """Request body definition to add an orientation of the UB calculation."""

    hkl: HklModel
    xyz: XyzModel
    position: Optional[PositionModel] = None


class EditReflectionParams(BaseModel):
    """Request body definition to edit a reflection of the UB calculation."""

    hkl: Optional[HklModel] = None
    position: Optional[PositionModel] = None
    energy: Optional[float] = None
    set_tag: Optional[str] = None


class EditOrientationParams(BaseModel):
    """Request body definition to edit an orientation of the UB calculation."""

    hkl: Optional[HklModel] = None
    xyz: Optional[XyzModel] = None
    position: Optional[PositionModel] = None
    set_tag: Optional[str] = None


def select_idx_or_tag_str(idx: Optional[int], tag: Optional[str]) -> str:
    """Select an index or tag, and generate a string from it.

    Return a string for diffcalc_API.models.response.InfoResponse endpoint responses.
    """
    return f"index {idx}" if idx is not None else f"tag {tag}"
