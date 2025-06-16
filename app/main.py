# app/main.py

# --- Standard Library Imports ---
import logging
from contextlib import asynccontextmanager

# --- FastAPI Imports ---
from fastapi import FastAPI
# We need this to redirect the user from the main page to the docs page
from fastapi.responses import RedirectResponse

# --- Our Application's Imports ---
from app.api.router import api_router
from app.db.database import init_db
from app.services.vector_store import vector_store_service

# This sets up basic logging so we can see what's happening in the terminal.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
# We get a logger instance to use in this file.
logger = logging.getLogger(__name__)


# This is a special function that manages what happens when our app starts and stops.
# It's called a "lifespan" manager.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Code to run ON STARTUP ---
    logger.info("Application starting up...")

    # Initialize our connection to the MongoDB database.
    await init_db()
    logger.info("Database connection and Beanie ODM initialized.")

    # The vector_store_service gets created automatically when imported.
    # So, the AI model and FAISS index are loaded into memory here.
    logger.info("Vector store service is ready.")

    # This 'yield' is where the application will be running.
    yield

    # --- Code to run ON SHUTDOWN ---
    logger.info("Application shutting down...")

    # It's important to save our FAISS index to a file before the app closes.
    # This way, we don't have to rebuild it from scratch every time.
    vector_store_service.save_index()
    logger.info("FAISS index has been saved successfully.")


# This creates our main FastAPI application.
app = FastAPI(
    title="AI-Powered FAQ System",
    description="An API to ask questions about documents using AI, built with FastAPI.",
    version="1.0.0",
    # We tell FastAPI to use our lifespan manager for startup and shutdown tasks.
    lifespan=lifespan,
)


# This is a user-friendly feature.
# If someone goes to the main URL ("/"), we automatically redirect them to the API docs.
@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")


# This line includes all the API endpoints (like /documents, /query, etc.)
# that we defined in our `api` folder. It keeps our main file clean.
app.include_router(api_router)