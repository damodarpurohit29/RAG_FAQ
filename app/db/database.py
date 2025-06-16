# app/db/database.py

import motor.motor_asyncio
# STEP 1: We must import 'IndexModel' and 'ASCENDING' from pymongo.
from pymongo import IndexModel, ASCENDING
from beanie import init_beanie, Document as BeanieDocument
from typing import Optional

from app.core.config import settings


# This class defines the structure of a document in our MongoDB "documents" collection.
class DocumentDB(BeanieDocument):
    # This part is correct and does not need to change.
    faiss_id: Optional[int] = None
    filename: str
    content: str

    class Settings:
        # The name of the collection (like a table in SQL) in MongoDB.
        name = "documents"

        # STEP 2: THIS IS THE FINAL FIX.
        # We replace the old 'indexes' list with this one, which uses the
        # official pymongo.IndexModel class. This is the correct way.
        indexes = [
            IndexModel(
                [("faiss_id", ASCENDING)],
                name="faiss_id_unique_index", # Give the index a clear name
                unique=True                  # Enforce the unique constraint
            )
        ]


# This function connects to the database.
# It does not need to change.
async def init_db():
    # Create a client to connect to MongoDB.
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.DATABASE_URL)

    # Initialize Beanie. It will now correctly create the index we defined above.
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[DocumentDB]
    )