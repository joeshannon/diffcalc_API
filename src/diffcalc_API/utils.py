import pickle
from pathlib import Path

from diffcalc.hkl.calc import HklCalculation
from fastapi import HTTPException

savePicklesFolder = "/dls/tmp/ton99817/diffcalc_pickles"
VectorProperties = ["n_hkl", "n_phi", "surf_nhkl", "surf_nphi"]
pickledNames = {"ub", "constraints", "hkl"}
constraintsWithNoValue = {"a_eq_b", "bin_eq_bout", "mu_is_gam", "bisect"}

allConstraints = {
    "delta",
    "gam" "qaz",
    "naz",
    "a_eq_b",
    "alpha",
    "beta",
    "psi",
    "bin_eq_bout",
    "betain",
    "betaout",
    "mu",
    "eta",
    "chi",
    "phi",
    "mu_is_gam",
    "bisect",
    "omega",
}


def unpickleHkl(name: str) -> HklCalculation:
    pickledFile = Path(savePicklesFolder) / name
    check_file_exists(pickledFile, name)

    with open(pickledFile, "rb") as openedFile:
        diffcalcObject: HklCalculation = pickle.load(openedFile)

    return diffcalcObject


def check_file_exists(pickledFile: Path, name: str) -> None:
    if not (pickledFile).is_file():
        errorMessage = (
            f"File for crystal {name} not found."
            f"\nYou need to post to"
            f" http://localhost:8000/{name}"
            f" first to generate the pickled file.\n"
        )
        raise HTTPException(status_code=401, detail=errorMessage)


def pickleHkl(object: HklCalculation, pickleFileName: str) -> Path:
    pickleFilePath = Path(savePicklesFolder) / pickleFileName
    with open(pickleFilePath, "wb") as pickleFile:
        pickle.dump(obj=object, file=pickleFile)

    return pickleFilePath


def deletePickle(pickleFileName) -> Path:
    pickleFilePath = Path(savePicklesFolder) / pickleFileName
    Path(pickleFilePath).unlink()

    return pickleFilePath
