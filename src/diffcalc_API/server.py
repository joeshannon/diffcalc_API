# This starts the server, and sets up the appropriate routes.
# in future consider separating these functionalities.
# import os
from pathlib import Path
from typing import Optional, Tuple, Union

from diffcalc.hkl.geometry import Position
from diffcalc.ub.calc import UBCalculation
from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

saveFolder = "/dls/tmp/ton99817/diffcalc_pickles"

VectorProperties = ["n_hkl", "n_phi", "surf_nhkl", "surf_nphi"]


class ResponseModel(BaseModel):
    calculation: UBCalculation

    class Config:
        arbitrary_types_allowed = True


# now that we're pickling, define pydantic models for inputs/returns and
# just let the pickling handle the objects.


class setLatticeParamsModel(BaseModel):
    system: Optional[Union[str, float]] = None
    a: Optional[float] = None
    b: Optional[float] = None
    c: Optional[float] = None
    alpha: Optional[float] = None
    beta: Optional[float] = None
    gamma: Optional[float] = None


class addReflectionParamsModel(BaseModel):
    hkl: Tuple[float, float, float]
    position: Tuple[
        float, float, float, float, float, float
    ]  # allows easier user input
    energy: float
    tag: Optional[str] = None


class addOrientationParamsModel(BaseModel):
    hkl: Tuple[float, float, float]
    xyz: Tuple[float, float, float]
    position: Optional[Tuple[float, float, float, float, float, float]] = None
    tag: Optional[str] = None


@app.post("/calc/{name}")
async def make_calc(name: str):
    calc = UBCalculation(name=name)
    calc.pickle(Path(saveFolder) / name)
    return {"message": "processed"}


@app.put("/calc/{name}/set/lattice")
async def set_lattice(
    name: str,
    setLatticeParams: setLatticeParamsModel = Body(example={"a": 4.913, "c": 5.405}),
):
    # step 1. Does the pickled file already exist?
    print(setLatticeParams)
    if not (Path(saveFolder) / name).is_file():
        errorMessage = (
            f"you need to call /calc/{name} first to generate the pickled file."
        )
        raise HTTPException(status_code=401, detail=errorMessage)

    # step 2. Unpickle the file if it does.
    calc = UBCalculation.load(Path(saveFolder) / name)
    try:
        calc.set_lattice(name=name, **setLatticeParams.dict())
    except Exception as e:
        raise HTTPException(status_code=450, detail=f"something happened: {e}")

    calc.pickle(Path(saveFolder) / name)
    return {"message": "processed"}


# app.post() with ability to set any property, like n_hkl.
@app.put("/calc/{name}/set/property/{property}")
async def modify_property(
    name: str,
    property: str,
    targetValue: Tuple[float, float, float] = Body(..., example=[1, 0, 0]),
):
    # first, need to check that 1. the property exists and 2. the property type is the
    # same as targetValue type.
    if property not in VectorProperties:
        raise HTTPException(
            status_code=401,
            detail=f"invalid property. Choose one of: {VectorProperties}",
        )

    if not (Path(saveFolder) / name).is_file():
        errorMessage = (
            f"you need to call /calc/{name} first to generate the pickled file."
        )
        raise HTTPException(status_code=401, detail=errorMessage)

    calc = UBCalculation.load(Path(saveFolder) / name)
    try:
        setattr(calc, property, targetValue)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"something happened: {e}")

    calc.pickle(Path(saveFolder) / name)
    return {"message": "processed"}


@app.put("/calc/{name}/add/reflection")
async def add_reflection(
    name: str,
    addReflectionParams: addReflectionParamsModel = Body(
        ...,
        example={
            "hkl": [0, 0, 1],
            "position": [7.31, 0.0, 10.62, 0, 0.0, 0],
            "energy": 12.39842,
            "tag": "refl1",
        },
    ),
):
    if not (Path(saveFolder) / name).is_file():
        errorMessage = (
            f"you need to call /calc/{name} first to generate the pickled file."
        )
        raise HTTPException(status_code=401, detail=errorMessage)

    calc = UBCalculation.load(Path(saveFolder) / name)

    try:
        calc.add_reflection(
            addReflectionParams.hkl,
            Position(*addReflectionParams.position),
            addReflectionParams.energy,
            addReflectionParams.tag,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"something happened: {e}")

    calc.pickle(Path(saveFolder) / name)
    return {"message": "processed"}


@app.put("/calc/{name}/add/orientation")
async def add_orientation(
    name: str,
    addOrientationParams: addOrientationParamsModel = Body(
        ...,
        example={
            "hkl": [0, 1, 0],
            "xyz": [0, 1, 0],
            "tag": "plane",
        },
    ),
):
    if not (Path(saveFolder) / name).is_file():
        errorMessage = (
            f"you need to call /calc/{name} first to generate the pickled file."
        )
        raise HTTPException(status_code=401, detail=errorMessage)

    calc = UBCalculation.load(Path(saveFolder) / name)
    position = (
        Position(*addOrientationParams.position)
        if addOrientationParams.position
        else None
    )

    try:
        calc.add_orientation(
            addOrientationParams.hkl,
            addOrientationParams.xyz,
            position,
            addOrientationParams.tag,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"something happened: {e}")

    calc.pickle(Path(saveFolder) / name)
    return {"message": "processed"}


@app.get("/calc/{name}/UB")
async def calculate_UB(
    name: str, firstTag: Optional[str] = None, secondTag: Optional[str] = None
):
    if not (Path(saveFolder) / name).is_file():
        errorMessage = (
            f"you need to call /calc/{name} first to generate the pickled file."
        )
        raise HTTPException(status_code=401, detail=errorMessage)

    calc = UBCalculation.load(Path(saveFolder) / name)

    calc.calc_ub(firstTag, secondTag)

    calc.pickle(Path(saveFolder) / name)
    print(calc.UB)
    return {"message": "processed"}
