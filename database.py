import os
from motor.motor_asyncio import AsyncIOMotorClient

# This looks for an environment variable. 
# Inside Docker, we will name the host 'mongodb'.
# If you run it locally, it defaults to 'localhost'.
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGODB_URL)
db = client.transaction_db
collection = db.transactions