from pymongo import MongoClient
from pymongo.database import Database

client: MongoClient = MongoClient()
database: Database = client.test_db
