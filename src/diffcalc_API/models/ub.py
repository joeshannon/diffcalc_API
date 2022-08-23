from typing import Optional

from pydantic import BaseModel


class HklModel(BaseModel):
    h: float
    k: float
    l: float


class XyzModel(BaseModel):
    x: float
    y: float
    z: float


class PositionModel(BaseModel):
    mu: float
    delta: float
    nu: float
    eta: float
    chi: float
    phi: float


class SetLatticeParams(BaseModel):
    name: Optional[str] = None
    system: Optional[str] = None
    a: Optional[float] = None
    b: Optional[float] = None
    c: Optional[float] = None
    alpha: Optional[float] = None
    beta: Optional[float] = None
    gamma: Optional[float] = None


class AddReflectionParams(BaseModel):
    hkl: HklModel
    position: PositionModel
    energy: float


class AddOrientationParams(BaseModel):
    hkl: HklModel
    xyz: XyzModel
    position: Optional[PositionModel] = None


class EditReflectionParams(BaseModel):
    hkl: Optional[HklModel] = None
    position: Optional[PositionModel] = None
    energy: Optional[float] = None
    set_tag: Optional[str] = None


class EditOrientationParams(BaseModel):
    hkl: Optional[HklModel] = None
    xyz: Optional[XyzModel] = None
    position: Optional[PositionModel] = None
    set_tag: Optional[str] = None


def select_idx_or_tag_str(idx: Optional[int], tag: Optional[str]):
    return f"index {idx}" if idx is not None else f"tag {tag}"
