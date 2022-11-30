from dataclasses import dataclass
from typing import Optional

from diffcalc_api.types.Position import Position


@dataclass
class Reflection:
    h: float
    k: float
    l: float
    pos: Position
    energy: float
    tag: Optional[str]
