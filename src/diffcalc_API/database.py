import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseSettings


class Settings(BaseSettings):
    mongo_url: str = "localhost:27017"


settings = Settings()

client: AsyncIOMotorClient = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_url)
database: AsyncIOMotorDatabase = client.test_db
