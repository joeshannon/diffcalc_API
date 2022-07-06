from fastapi import FastAPI

from .routes import Constraints, HklCalculation, UBCalculation

app = FastAPI()
app.include_router(UBCalculation.router)
app.include_router(Constraints.router)
app.include_router(HklCalculation.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
