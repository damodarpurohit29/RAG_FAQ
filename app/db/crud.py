# app/db/crud.py

from typing import List
from .database import DocumentDB
from app.models import schemas

# Note: All these functions are 'async' because our database driver 'motor'
# is asynchronous. This is good for performance.

async def get_next_faiss_id() -> int:
    """
    Finds the document with the highest faiss_id and returns the next number.
    This gives us a unique integer ID for each new document.
    """
    # Sort documents by faiss_id in descending order and get the first one.
    last_doc = await DocumentDB.find_one(sort=[("faiss_id", -1)])
    # If a document was found, add 1 to its ID. If not, start at 0.
    return (last_doc.faiss_id + 1) if last_doc and last_doc.faiss_id is not None else 0

async def get_document_by_faiss_id(faiss_id: int) -> DocumentDB | None:
    """Finds a single document using its special faiss_id."""
    return await DocumentDB.find_one(DocumentDB.faiss_id == faiss_id)

async def get_all_documents(skip: int = 0, limit: int = 100) -> List[DocumentDB]:
    """Gets a list of all documents from the database."""
    return await DocumentDB.find_all(skip=skip, limit=limit).to_list()

async def create_document(doc: schemas.DocumentCreate) -> DocumentDB:
    """
    Creates a new document in the database.
    It first figures out the next available faiss_id.
    """
    next_id = await get_next_faiss_id()
    db_document = DocumentDB(
        filename=doc.filename,
        content=doc.content,
        faiss_id=next_id
    )
    # Save the new document to the database.
    await db_document.insert()
    return db_document