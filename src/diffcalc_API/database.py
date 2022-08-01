import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

client: AsyncIOMotorClient = motor.motor_asyncio.AsyncIOMotorClient(
    "172.23.169.16:27017"
)
database: AsyncIOMotorDatabase = client.test_db
