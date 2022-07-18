from typing import Optional, Tuple, Union

from pydantic import BaseModel


class SetLatticeParams(BaseModel):
    system: Optional[Union[str, float]] = None
    a: Optional[float] = None
    b: Optional[float] = None
    c: Optional[float] = None
    alpha: Optional[float] = None
    beta: Optional[float] = None
    gamma: Optional[float] = None


class AddReflectionParams(BaseModel):
    hkl: Tuple[float, float, float]
    position: Tuple[
        float, float, float, float, float, float
    ]  # allows easier user input
    energy: float
    tag: Optional[str] = None


class AddOrientationParams(BaseModel):
    hkl: Tuple[float, float, float]
    xyz: Tuple[float, float, float]
    position: Optional[Tuple[float, float, float, float, float, float]] = None
    tag: Optional[str] = None


class EditReflectionParams(BaseModel):
    hkl: Optional[Tuple[float, float, float]] = None
    position: Optional[Tuple[float, float, float, float, float, float]] = None
    energy: Optional[float] = None
    tag_or_idx: Union[int, str]


class EditOrientationParams(BaseModel):
    hkl: Optional[Tuple[float, float, float]] = None
    xyz: Optional[Tuple[float, float, float]] = None
    position: Optional[Tuple[float, float, float, float, float, float]] = None
    tag_or_idx: Union[int, str]


class DeleteParams(BaseModel):
    tag_or_idx: Union[int, str]
