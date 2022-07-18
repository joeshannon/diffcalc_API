import numpy as np

from diffcalc_API.config import ALL_CONSTRAINTS
from diffcalc_API.errors.definitions import (
    ALL_RESPONSES,
    DiffcalcAPIException,
    ErrorCodes,
)


class Codes(ErrorCodes):
    CHECK_CONSTRAINT_EXISTS = 400


responses = {code: ALL_RESPONSES[code] for code in np.unique(Codes().all_codes())}


def check_constraint_exists(constraint: str) -> None:
    if constraint not in ALL_CONSTRAINTS:
        raise DiffcalcAPIException(
            status_code=Codes.CHECK_CONSTRAINT_EXISTS,
            detail=(
                f"property {constraint} does not exist as a valid constraint."
                f" Choose one of {ALL_CONSTRAINTS}"
            ),
        )
