# app/services/rag_service.py

# --- Standard Library Imports ---
import logging

# --- Third-party Imports ---
# This is the new, modern way to use the OpenAI library.
# We import the special 'AsyncOpenAI' client that works well with FastAPI.
from openai import AsyncOpenAI

# --- Our Application's Imports ---
from app.core.config import settings
from app.db import crud
from app.models import schemas
from .vector_store import vector_store_service

# We get a logger instance to use in this file.
logger = logging.getLogger(__name__)

# Create a single, specific client for talking to OpenAI.
# This is better than setting a global key. We tell it our secret key from the settings.
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


# This is the main "brain" of our RAG system.
async def query_rag(query: str) -> schemas.QueryResponse:
    """
    This function handles the whole RAG process from start to finish.
    RAG stands for Retrieval-Augmented Generation.
    """
    logger.info(f"Starting RAG process for query: '{query}'")

    # --- Step 1: RETRIEVAL ---
    # We "retrieve" or "get" the most relevant documents for the user's question.
    # Our vector_store_service does the search and gives us back the IDs.
    retrieved_faiss_ids = vector_store_service.search(query, k=3)

    # If the search didn't find any matching documents, we stop here.
    if not retrieved_faiss_ids:
        logger.warning("RAG: No documents were found by the vector search.")
        return schemas.QueryResponse(
            answer="I couldn't find any relevant documents to answer your question.",
            source_documents=[]
        )

    # Get the full text of the documents from our MongoDB database using the IDs we found.
    retrieved_docs = []
    for faiss_id in retrieved_faiss_ids:
        # We need to use 'await' because our database functions are async.
        doc = await crud.get_document_by_faiss_id(faiss_id=faiss_id)
        if doc:
            retrieved_docs.append(doc)

    # --- Step 2: AUGMENTATION ---
    # We "augment" or "add to" the user's question with the information we found.
    # We combine all the document texts into a single "context" string.
    context = "\n\n---\n\n".join([doc.content for doc in retrieved_docs])

    # Now we build the big instruction (the "prompt") for the AI.
    prompt = f"""
    You are a helpful AI assistant. Please answer the user's question based ONLY on the context provided below.
    If the information is not in the context, please say: "I don't have enough information to answer."

    Context:
    {context}

    Question: {query}

    Answer:
    """

    # --- Step 3: GENERATION ---
    # We ask the AI to "generate" or "create" a final answer.
    # We use a 'try...except' block as a safety net in case the OpenAI website is down or our key is wrong.
    try:
        # We send our prompt to the OpenAI API using the client we created.
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Lower temperature = more factual, less "creative" answers.
        )
        # We get the text part of the AI's response.
        answer = response.choices[0].message.content.strip()

    except Exception as e:
        # If anything goes wrong with the API call, this 'except' block will run.
        logger.error(f"RAG: The OpenAI API call failed. Error: {e}")
        # We set a safe, user-friendly error message.
        answer = "Sorry, there was an error talking to the AI."

    # Prepare the final response object, including the documents we used as sources.
    source_docs_response = [schemas.DocumentResponse.model_validate(doc) for doc in retrieved_docs]

    return schemas.QueryResponse(answer=answer, source_documents=source_docs_response)