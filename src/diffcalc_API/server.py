from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints
from diffcalc.ub.calc import UBCalculation
from diffcalc.util import DiffcalcException
from fastapi import FastAPI, Request, responses

from diffcalc_API import errors
from diffcalc_API.errors import DiffcalcAPIException
from diffcalc_API.utils import deletePickle, pickleHkl

from . import routes

app = FastAPI(responses=errors.responses)
app.include_router(routes.UBCalculation.router)
app.include_router(routes.Constraints.router)
app.include_router(routes.HklCalculation.router)

#######################################################################################
#                              Middleware for Exceptions                              #
#######################################################################################


@app.exception_handler(DiffcalcException)
async def diffcalc_exception_handler(request: Request, exc: DiffcalcException):
    return responses.JSONResponse(
        status_code=428,
        content={"message": exc.__str__(), "type": str(type(exc))},
    )


@app.exception_handler(DiffcalcAPIException)
async def http_exception_handler(request: Request, exc: DiffcalcAPIException):
    return responses.JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "type": str(type(exc))},
    )


async def server_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # you probably want some kind of logging here

        return responses.JSONResponse(
            status_code=500,
            content={"message": e.__str__(), "type": str(type(e))},
        )


app.middleware("http")(server_exceptions_middleware)


#######################################################################################
#                                    Global Routes                                    #
#######################################################################################


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
