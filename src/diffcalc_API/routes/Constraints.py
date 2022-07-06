import pickle
from typing import Dict, Tuple, Union

from diffcalc.hkl.constraints import Constraints
from fastapi import APIRouter, Body

# from diffcalc_API.utils import OpenCalculation, savePicklesFolder
from diffcalc_API.utils import OpenPickle, constraintsWithNoValue, makePickleFile

ConstraintObject = OpenPickle("constraints")
router = APIRouter(prefix="/constraints", tags=["constraints"])


# Collection is not supported, so I explicitly define it here.
singleConstraintType = Union[Tuple[str, float], str]


@router.post("/create/{name}")
async def make_constraints(
    name: str,
    constraintDict: Dict[str, Union[float, bool]] = Body(
        example={"qaz": 0, "a_eq_b": True, "eta": 0}
    ),
):
    booleanConstraints = set(constraintDict.keys()).intersection(constraintsWithNoValue)
    for constraint in booleanConstraints:
        constraintDict[constraint] = bool(constraintDict[constraint])

    constraints = Constraints(constraintDict)

    pickleFileName = makePickleFile(name, "constraints")

    with open(pickleFileName, "wb") as pickleFile:
        pickle.dump(obj=constraints, file=pickleFile)

    return {"message": "complete"}
