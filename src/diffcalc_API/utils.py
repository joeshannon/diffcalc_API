import pickle
from pathlib import Path
from typing import Union

from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation
from fastapi import HTTPException

# from typing import Any, Union, cast


savePicklesFolder = "/dls/tmp/ton99817/diffcalc_pickles"
VectorProperties = ["n_hkl", "n_phi", "surf_nhkl", "surf_nphi"]
pickledNames = {"ub", "constraints", "hkl"}
constraintsWithNoValue = {"a_eq_b", "bin_eq_bout", "mu_is_gam", "bisect"}


class OpenPickle:
    def __init__(self, diffcalcObjectName: str):
        if diffcalcObjectName in pickledNames:
            self.diffcalcObjectName = diffcalcObjectName
        else:
            self.diffcalcObjectName = "ub"

    def _check_file_exists(self, pickledFile: Path, name: str) -> None:
        if not (pickledFile).is_file():
            errorMessage = (
                f"{self.diffcalcObjectName} for this crystal ({name}) not found."
                f"\nYou need to post to"
                f" http://localhost:8000/{self.diffcalcObjectName}/create/{name}"
                f" first to generate the pickled file.\n"
            )
            raise HTTPException(status_code=401, detail=errorMessage)

    def _unpickle_file(
        self, pickledFile: Path
    ) -> Union[UBCalculation, Constraints, HklCalculation]:
        with open(pickledFile, "rb") as openedFile:
            rawObject: Union[UBCalculation, Constraints, HklCalculation] = pickle.load(
                openedFile
            )

        return rawObject

    def __call__(
        self,
        name: str,
    ):
        pickledFile = Path(savePicklesFolder) / name / self.diffcalcObjectName
        self._check_file_exists(pickledFile, name)

        # I want to be explicit about the types of objects this method will return,
        # which depends on self.diffcalcObjectName.
        # TODO: is there a way to achieve this? Is it needed?

        diffcalcObject = self._unpickle_file

        # if self.diffcalcObjectName == "ub":
        #     diffcalcObject = cast(UBCalculation, rawObject)
        # elif self.diffcalcObjectName == "constraints":
        #     diffcalcObject = cast(Constraints, rawObject)
        # elif self.diffcalcObjectName == "hkl":
        #     diffcalcObject = cast(HklCalculation, rawObject)

        return diffcalcObject


class returnHkl:
    def __init__(self, name: str):
        self.pickleFileName = makePickleFile(name, "hkl")
        self.pickleJar = self.pickleFileName.parent

    def __call__(self):
        if Path(self.pickleFileName).exists():
            with open(self.pickleFileName, "rb") as pickleFile:
                pickleData = pickle.load(pickleFile)

            return pickleData
        return None


def makePickleFile(crystalName: str, pickleName: str):
    pickleFile = Path(savePicklesFolder) / crystalName / pickleName

    if not pickleFile.parent.exists():
        Path(pickleFile.parent).mkdir()

    return pickleFile
