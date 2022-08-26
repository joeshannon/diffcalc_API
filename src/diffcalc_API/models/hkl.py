"""Defines pydantic models relating to hkl endpoints."""

from dataclasses import dataclass
from typing import Iterator, List, Optional, Union

from diffcalc.hkl.geometry import Position


@dataclass
class SolutionConstraints:
    """Class to store solution constraints.

    The diffraction angle calculator often provides multiple diffractometer
    angles as equivalent to a set of miller indices. Solution bounds can be provided
    to constrain these, however they must pass some checks before use.

    Solutions are constrained by diffractometer angles, or axes. A high bound and low
    bound must be given for each provided. All three of these conditions must contain
    the same number of elements to be valid.
    """

    axes: Optional[List[str]] = None
    low_bound: Optional[List[float]] = None
    high_bound: Optional[List[float]] = None
    valid: bool = True
    msg: str = ""

    def __post_init__(self):
        """Immediately upon initialisation, evaluate validity of bounds."""
        self.invalid_bounds()

    def invalid_bounds(self) -> None:
        """Compute if the inputes are valid.

        If not, sets self.valid to False.
        """
        axes, low_bound, high_bound = self.axes, self.low_bound, self.high_bound
        msg = self.msg

        if axes and low_bound and high_bound:
            iterator: Iterator[Union[List[str], List[float]]] = iter(
                [axes, low_bound, high_bound]
            )
            length = len(next(iterator))
            same_length = all(len(each_list) == length for each_list in iterator)

            if not same_length:
                msg = "queries axes, low_bound and high_bound are not the same length."

            if not all(angle in Position.fields for angle in axes):
                msg = (
                    "query {axes} contains an angle which is not a subset of "
                    + f"{Position.fields}"
                )

        elif axes or low_bound or high_bound:
            msg = (
                "If bounds are provided, a list of axes, low bounds and high bounds "
                + "must be provided as query parameters."
            )

        self.msg = msg
        if self.msg:
            self.valid = False
