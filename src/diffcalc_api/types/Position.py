from dataclasses import dataclass


@dataclass
class Position:
    """Diffractometer angles in degrees."""

    mu: float
    delta: float
    nu: float
    eta: float
    chi: float
    phi: float
