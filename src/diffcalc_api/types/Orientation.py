from dataclasses import dataclass
from typing import Optional

from diffcalc_api.types.Position import Position


@dataclass
class Orientation:
    h: float
    k: float
    l: float
    x: float
    y: float
    z: float
    pos: Position
    tag: Optional[str]
