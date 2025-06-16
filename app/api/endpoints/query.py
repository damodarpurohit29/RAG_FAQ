# app/api/endpoints/query.py

from fastapi import APIRouter, HTTPException, status
import logging

from app.models import schemas
from app.services import rag_service

logger = logging.getLogger(__name__)
router = APIRouter()


# A simple health check endpoint to see if the server is running.
@router.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
def health_check():
    return {"status": "ok"}


# The main endpoint for asking questions.
@router.post("/query", response_model=schemas.QueryResponse, tags=["RAG"])
async def handle_query(query: schemas.QueryRequest):
    """
    API endpoint to handle a user's question.
    It triggers the RAG service to find an answer.
    """
    if not query.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    logger.info(f"API: Received query: '{query.question}'")
    try:
        response = await rag_service.query_rag(query.question)
        return response
    except Exception as e:
        logger.error(f"API: Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while processing your query.")