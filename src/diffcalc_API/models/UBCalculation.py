from typing import Optional, Tuple, Union

from pydantic import BaseModel


class setLatticeParams(BaseModel):
    system: Optional[Union[str, float]] = None
    a: Optional[float] = None
    b: Optional[float] = None
    c: Optional[float] = None
    alpha: Optional[float] = None
    beta: Optional[float] = None
    gamma: Optional[float] = None


class addReflectionParams(BaseModel):
    hkl: Tuple[float, float, float]
    position: Tuple[
        float, float, float, float, float, float
    ]  # allows easier user input
    energy: float
    tag: Optional[str] = None


class addOrientationParams(BaseModel):
    hkl: Tuple[float, float, float]
    xyz: Tuple[float, float, float]
    position: Optional[Tuple[float, float, float, float, float, float]] = None
    tag: Optional[str] = None
