import numpy as np

from diffcalc_API.config import all_constraints
from diffcalc_API.errors.definitions import (
    DiffcalcAPIException,
    ErrorCodes,
    all_responses,
)


class Codes(ErrorCodes):
    check_constraint_exists = 400


responses = {code: all_responses[code] for code in np.unique(Codes().all_codes())}


def check_constraint_exists(constraint: str) -> None:
    if constraint not in all_constraints:
        raise DiffcalcAPIException(
            status_code=Codes.check_constraint_exists,
            detail=(
                f"property {constraint} does not exist as a valid constraint."
                f" Choose one of {all_constraints}"
            ),
        )
