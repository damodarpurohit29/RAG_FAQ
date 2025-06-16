# app/models/schemas.py

# --- Pydantic and Typing Imports ---
from pydantic import BaseModel, Field, field_validator
from typing import List, Any

# --- BSON Imports (for MongoDB's ObjectId) ---
# We need this for the type hint in our validator
from bson import ObjectId


# This defines what the user needs to send when uploading a document.
class DocumentCreate(BaseModel):
    filename: str
    content: str


# This defines how we will format a document when we send it back to the user.
# It includes the ID that the database gives it.
class DocumentResponse(BaseModel):
    # We still use the alias to get the data from the '_id' field of the database object.
    id: str = Field(..., alias="_id")
    filename: str
    content: str
    faiss_id: int

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        """
        Custom validator to convert MongoDB's ObjectId to a string.
        Pydantic runs this BEFORE trying to validate the field.
        """
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        # This allows Pydantic to create the model from a database object.
        from_attributes = True

        # This allows the use of aliases like '_id' during model creation.
        populate_by_name = True


# This is what the user sends when they ask a question.
class QueryRequest(BaseModel):
    question: str


# This is the final answer we send back to the user.
class QueryResponse(BaseModel):
    answer: str
    # We also include the documents we used to find the answer.
    source_documents: List[DocumentResponse]