from typing import Optional, Union

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
    system: Optional[Union[str, float]] = None
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
    tag: Optional[str] = None


class AddOrientationParams(BaseModel):
    hkl: HklModel
    xyz: XyzModel
    position: Optional[PositionModel] = None
    tag: Optional[str] = None


class EditReflectionParams(BaseModel):
    hkl: Optional[HklModel] = None
    position: Optional[PositionModel] = None
    energy: Optional[float] = None
    retrieve_tag: Optional[str] = None
    retrieve_idx: Optional[int] = None
    set_tag: Optional[str] = None


class EditOrientationParams(BaseModel):
    hkl: Optional[HklModel] = None
    xyz: Optional[XyzModel] = None
    position: Optional[PositionModel] = None
    retrieve_tag: Optional[str] = None
    retrieve_idx: Optional[int] = None
    set_tag: Optional[str] = None
