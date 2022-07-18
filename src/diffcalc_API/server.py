from diffcalc.util import DiffcalcException
from fastapi import Depends, FastAPI, Request, responses

from diffcalc_API.errors.constraints import responses as constraints_responses
from diffcalc_API.errors.definitions import DiffcalcAPIException
from diffcalc_API.errors.hkl import responses as hkl_responses
from diffcalc_API.errors.ub import responses as ub_responses
from diffcalc_API.stores.pickling import get_store

from . import routes

app = FastAPI(responses=get_store().responses)

app.include_router(routes.ub.router, responses=ub_responses)
app.include_router(routes.constraints.router, responses=constraints_responses)
app.include_router(routes.hkl.router, responses=hkl_responses)

#######################################################################################
#                              Middleware for Exceptions                              #
#######################################################################################


@app.exception_handler(DiffcalcException)
async def diffcalc_exception_handler(request: Request, exc: DiffcalcException):
    return responses.JSONResponse(
        status_code=400,
        content={"message": str(exc), "type": str(type(exc))},
    )


@app.exception_handler(DiffcalcAPIException)
async def http_exception_handler(request: Request, exc: DiffcalcAPIException):
    return responses.JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "type": str(type(exc))},
    )


@app.middleware("http")
async def server_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # you probably want some kind of logging here

        return responses.JSONResponse(
            status_code=500,
            content={"message": str(e), "type": str(type(e))},
        )


#######################################################################################
#                                    Global Routes                                    #
#######################################################################################


@app.post("/{name}")
async def create_hkl_object(name: str, repo=Depends(get_store)):
    await repo.create(name)

    return {"message": f"file for crystal {name} created"}


@app.delete("/{name}")
async def delete_hkl_object(name: str, repo=Depends(get_store)):
    await repo.delete(name)

    return {"message": f"file for crystal {name} deleted"}
