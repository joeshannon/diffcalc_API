from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation
from diffcalc.util import DiffcalcException
from fastapi import FastAPI, Request, Response

from diffcalc_API.utils import deletePickle, pickleHkl

from . import routes

app = FastAPI()
app.include_router(routes.UBCalculation.router)
app.include_router(routes.Constraints.router)
app.include_router(routes.HklCalculation.router)

# middleware for server exception handling:


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # you probably want some kind of logging here
        if isinstance(e, DiffcalcException):
            return Response(f"{e}", status_code=401)

        return Response("Internal Server Error", status_code=500)


app.middleware("http")(catch_exceptions_middleware)


# Global routes
@app.post("/{name}")
async def save_hkl_object(name: str):
    UBcalc = UBCalculation(name=name)
    constraints = Constraints()
    hkl = HklCalculation(UBcalc, constraints)

    pickleLocation = pickleHkl(hkl, name)

    return {"message": f"file created at {pickleLocation}"}


@app.delete("/{name}")
async def delete_hkl_object(name: str):
    pickleLocation = deletePickle(name)

    return {"message": f"file at location {pickleLocation} deleted"}
