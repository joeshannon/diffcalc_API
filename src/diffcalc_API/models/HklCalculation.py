from typing import List, Tuple, Union

from pydantic import BaseModel

positionType = Tuple[float, float, float]


class labPosFromMillerParams(BaseModel):
    indices: Union[List[positionType], positionType]
    wavelength: float


class millerPosFromLabParams(BaseModel):
    labPosition: Tuple[float, float, float, float, float, float]
    wavelength: float
