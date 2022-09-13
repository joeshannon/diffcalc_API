from dataclasses import dataclass
from typing import Dict, List, Optional

from diffcalc.ub.calc import ReferenceVector
from pydantic import BaseModel
from typing_extensions import TypedDict


@dataclass
class PositionType:
    mu: float
    delta: float
    nu: float
    eta: float
    chi: float
    phi: float


class ReflectionType(TypedDict):
    h: float
    k: float
    l: float
    pos: PositionType
    energy: float
    tag: Optional[str]


class OrientationType(TypedDict):
    h: float
    k: float
    l: float
    x: float
    y: float
    z: float
    pos: PositionType
    tag: Optional[str]


@dataclass
class CrystalType:
    name: str
    system: str
    a: float  # pylint: disable=invalid-name
    b: float  # pylint: disable=invalid-name
    c: float  # pylint: disable=invalid-name
    alpha: float
    beta: float
    gamma: float


class UbCalcType(TypedDict):
    name: str
    crystal: Optional[CrystalType]
    reflist: List[ReflectionType]
    orientlist: List[OrientationType]
    reference: ReferenceVector
    surface: ReferenceVector
    u_matrix: Optional[List[List[float]]]
    ub_matrix: Optional[List[List[float]]]


class HklType(BaseModel):
    id: str
    ubcalc: UbCalcType
    constraints: Dict[str, float]
