import pymongo

client = pymongo.MongoClient()

database = client.test_db

collection = database.B07
