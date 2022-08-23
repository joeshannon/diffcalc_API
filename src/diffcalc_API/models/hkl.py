from dataclasses import dataclass
from typing import Iterator, List, Optional, Union

from diffcalc.hkl.geometry import Position


@dataclass
class SolutionConstraints:
    axes: Optional[List[str]] = None
    low_bound: Optional[List[float]] = None
    high_bound: Optional[List[float]] = None
    valid: bool = True
    msg: str = ""

    def __post_init__(self):
        self.invalid_bounds()

    def invalid_bounds(self) -> None:
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
