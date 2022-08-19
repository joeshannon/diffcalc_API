import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from diffcalc_API.config import Settings

settings = Settings()

client: AsyncIOMotorClient = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_url)
database: AsyncIOMotorDatabase = client.test_db
