from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation
from fastapi import FastAPI

from diffcalc_API.utils import pickleHkl

from . import routes

app = FastAPI()
app.include_router(routes.UBCalculation.router)
app.include_router(routes.Constraints.router)


@app.post("/create/{name}")
async def make_hkl_calculation(name: str):
    UBcalc = UBCalculation(name=name)
    constraints = Constraints()
    hkl = HklCalculation(UBcalc, constraints)

    pickleLocation = pickleHkl(hkl, name)

    return {"message": f"file created at {pickleLocation}"}


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
