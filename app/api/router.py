# app/api/router.py

from fastapi import APIRouter
from .endpoints import documents, query

# This is our main router for the entire API.
api_router = APIRouter()

# Include the endpoints from our other files.
# We can add a prefix, so all document routes will start with /documents.
api_router.include_router(query.router)
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])