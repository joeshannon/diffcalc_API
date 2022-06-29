from fastapi import FastAPI

from .routes import UBCalculation

app = FastAPI()
app.include_router(UBCalculation.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
