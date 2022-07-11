import pickle
from pathlib import Path

from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation

from diffcalc_API.config import savePicklesFolder
from diffcalc_API.errorDefinitions import attempting_to_overwrite, check_file_exists


def unpickleHkl(name: str) -> HklCalculation:
    pickleFilePath = Path(savePicklesFolder) / name
    check_file_exists(pickleFilePath, name)

    with open(pickleFilePath, "rb") as openedFile:
        diffcalcObject: HklCalculation = pickle.load(openedFile)

    return diffcalcObject


def pickleHkl(object: HklCalculation, pickleFileName: str) -> Path:
    pickleFilePath = Path(savePicklesFolder) / pickleFileName
    with open(pickleFilePath, "wb") as pickleFile:
        pickle.dump(obj=object, file=pickleFile)

    return pickleFilePath


def createPickle(pickleFileName: str) -> Path:
    attempting_to_overwrite(pickleFileName)

    UBcalc = UBCalculation(name=pickleFileName)
    constraints = Constraints()
    hkl = HklCalculation(UBcalc, constraints)

    pickleLocation = pickleHkl(hkl, pickleFileName)
    return pickleLocation


def deletePickle(pickleFileName: str) -> Path:
    pickleFilePath = Path(savePicklesFolder) / pickleFileName
    check_file_exists(pickleFilePath, pickleFileName)
    Path(pickleFilePath).unlink()

    return pickleFilePath
