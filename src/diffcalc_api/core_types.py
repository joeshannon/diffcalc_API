"""Exposes types of diffcalc-core objects."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Position:
    """Diffractometer angles in degrees.

    Similar to diffcalc.hkl.geometry.Position
    """

    mu: float
    delta: float
    nu: float
    eta: float
    chi: float
    phi: float


@dataclass
class Orientation:
    """Reference orientation of the sample.

    Similar to diffcalc.ub.reference.Orientation
    """

    h: float
    k: float
    l: float
    x: float
    y: float
    z: float
    pos: Position
    tag: Optional[str]


@dataclass
class Reflection:
    """Reference reflection of the sample.

    Similar to diffcalc.ub.reference.Reflection
    """

    h: float
    k: float
    l: float
    pos: Position
    energy: float
    tag: Optional[str]
