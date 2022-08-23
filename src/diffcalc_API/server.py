import logging
import traceback
from typing import Optional

from diffcalc.util import DiffcalcException
from fastapi import Depends, FastAPI, Query, Request, responses

from diffcalc_API import routes
from diffcalc_API.config import Settings
from diffcalc_API.errors.constraints import responses as constraints_responses
from diffcalc_API.errors.definitions import DiffcalcAPIException
from diffcalc_API.errors.hkl import responses as hkl_responses
from diffcalc_API.errors.ub import responses as ub_responses
from diffcalc_API.stores.protocol import get_store, setup_store

logger = logging.getLogger(__name__)
config = Settings()
setup_store("diffcalc_API.stores.mongo.MongoHklCalcStore")

app = FastAPI(
    responses=get_store().responses, title="diffcalc", version=config.api_version
)

app.include_router(routes.ub.router, responses=ub_responses)
app.include_router(routes.constraints.router, responses=constraints_responses)
app.include_router(routes.hkl.router, responses=hkl_responses)

#######################################################################################
#                              Middleware for Exceptions                              #
#######################################################################################


@app.exception_handler(DiffcalcException)
async def diffcalc_exception_handler(request: Request, exc: DiffcalcException):
    tb = traceback.format_exc()
    logging.warn(f"Diffcalc Exception caught by middleware: {tb}")

    return responses.JSONResponse(
        status_code=400,
        content={"message": str(exc), "type": str(type(exc))},
    )


@app.exception_handler(DiffcalcAPIException)
async def http_exception_handler(request: Request, exc: DiffcalcAPIException):
    tb = traceback.format_exc()
    logging.error(f"Diffcalc API Exception caught by middleware: {tb}")

    return responses.JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "type": str(type(exc))},
    )


@app.middleware("http")
async def server_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"General Exception caught by middleware: {tb}")

        return responses.JSONResponse(
            status_code=500,
            content={"message": str(e), "type": str(type(e))},
        )


#######################################################################################
#                                    Global Routes                                    #
#######################################################################################


@app.post("/{name}")
async def create_hkl_object(
    name: str,
    store=Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    await store.create(name, collection)

    return {"message": f"crystal {name} in collection {collection} created"}


@app.delete("/{name}")
async def delete_hkl_object(
    name: str,
    store=Depends(get_store),
    collection: Optional[str] = Query(default=None, example="B07"),
):
    await store.delete(name, collection)

    return {"message": f"crystal {name} in collection {collection} deleted"}
