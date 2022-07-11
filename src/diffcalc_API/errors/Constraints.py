import numpy as np

from diffcalc_API.config import allConstraints
from diffcalc_API.errorDefinitions import DiffcalcAPIException, ErrorCodes, allResponses


class codes(ErrorCodes):
    check_constraint_exists = 400


responses = {code: allResponses[code] for code in np.unique(codes().all_codes())}


def check_constraint_exists(constraint: str) -> None:
    if constraint not in allConstraints:
        raise DiffcalcAPIException(
            status_code=codes.check_constraint_exists,
            detail=(
                f"property {constraint} does not exist as a valid constraint."
                f" Choose one of {allConstraints}"
            ),
        )
