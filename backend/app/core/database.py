import os

from dotenv import load_dotenv
from pymongo import AsyncMongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")

if not MONGODB_URI or not MONGODB_DB:
    raise ValueError("MongoDB configuration is missing")


async def connect_to_mongodb(app):
    """Create MongoDB connection"""
    client = AsyncMongoClient(MONGODB_URI)

    #Verify that MongoDB is reachable
    await client.admin.command("ping")

    app.state.mongo_client = client
    app.state.db = client[MONGODB_DB]

    print("[INFO] Connected to MongoDB successfully.")

async def close_mongodb_connection(app):
    """Close mongodb connection"""

    await app.state.mongo_client.close()

    print("[INFO] MongoDB connection closed")

