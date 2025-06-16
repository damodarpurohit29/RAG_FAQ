# app/api/endpoints/documents.py

from fastapi import APIRouter, HTTPException, status
import logging
from typing import List

from app.db import crud
from app.models import schemas
from app.services.vector_store import vector_store_service

logger = logging.getLogger(__name__)
# An APIRouter helps organize endpoints into groups.
router = APIRouter()

# This defines the POST /documents/ endpoint.
@router.post("/", response_model=schemas.DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(doc: schemas.DocumentCreate):
    """
    API endpoint to upload a new document.
    It saves the doc to the database and adds its vector to the search index.
    """
    logger.info(f"API: Uploading document '{doc.filename}'")
    try:
        # Save to MongoDB
        db_document = await crud.create_document(doc=doc)
        # Add to FAISS search index
        vector_store_service.add_document(
            doc_id=db_document.faiss_id,
            content=db_document.content
        )
        # Use model_validate to create the response model instance correctly
        return schemas.DocumentResponse.model_validate(db_document)
    except Exception as e:
        logger.error(f"API: Error uploading document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not upload document.")

# This defines the GET /documents/ endpoint.
@router.get("/", response_model=List[schemas.DocumentResponse])
async def list_documents(skip: int = 0, limit: int = 10):
    """
    API endpoint to list all documents in the database.
    """
    logger.info("API: Listing documents")
    documents = await crud.get_all_documents(skip=skip, limit=limit)
    return [schemas.DocumentResponse.model_validate(doc) for doc in documents]