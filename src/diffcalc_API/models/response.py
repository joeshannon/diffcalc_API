from typing import Dict, List

from pydantic import BaseModel

from diffcalc_API.models.ub import HklModel


class InfoResponse(BaseModel):
    message: str


class StringResponse(BaseModel):
    payload: str


class ArrayResponse(BaseModel):
    payload: List[List[float]]


class ScanResponse(BaseModel):
    payload: Dict[str, List[Dict[str, float]]]


class DiffractorAnglesResponse(BaseModel):
    payload: List[Dict[str, float]]


class MillerIndicesResponse(BaseModel):
    payload: HklModel
