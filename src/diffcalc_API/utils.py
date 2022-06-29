from pathlib import Path

from diffcalc.ub.calc import UBCalculation
from fastapi import HTTPException

saveFolder = "/dls/tmp/ton99817/diffcalc_pickles"

VectorProperties = ["n_hkl", "n_phi", "surf_nhkl", "surf_nphi"]


class OpenCalculation:
    def __init__(self, calcType: str):
        self.calcType = calcType

    def __call__(
        self,
        name: str,
    ):
        if not (Path(saveFolder) / name / self.calcType).is_file():
            errorMessage = (
                f"you need to call /calc/{name} first to generate the pickled file."
            )
            raise HTTPException(status_code=401, detail=errorMessage)

        calc = UBCalculation.load(Path(saveFolder) / name / self.calcType)
        return calc
