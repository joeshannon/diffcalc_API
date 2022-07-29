import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

client: AsyncIOMotorClient = motor.motor_asyncio.AsyncIOMotorClient()
database: AsyncIOMotorDatabase = client.test_db
