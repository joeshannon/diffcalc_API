import pickle

from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation
from fastapi import APIRouter, Depends

# from diffcalc_API.utils import OpenCalculation, savePicklesFolder
# from diffcalc_API.utils import OpenPickle, makePickleFile, savePicklesFolder
from diffcalc_API.utils import OpenPickle, makePickleFile

# from pathlib import Path
# from typing import Dict, Tuple, Union


UBObject = OpenPickle("ub")
ConstraintObject = OpenPickle("constraints")
HklObject = OpenPickle("hkl")
router = APIRouter(prefix="/hkl", tags=["hkl"])


@router.post("/create/{name}")
async def make_hkl(
    name: str,
    UB: UBCalculation = Depends(UBObject),
    constraints: Constraints = Depends(ConstraintObject),
):
    calc = HklCalculation(UB, constraints)

    pickleFileName = makePickleFile(name, "hkl")

    with open(pickleFileName, "wb") as pickleFile:
        pickle.dump(obj=calc, file=pickleFile)

    print(calc)
    return {"message": "file created"}
