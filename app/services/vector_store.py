# app/services/vector_store.py

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# This class manages the vector index.
class VectorStoreService:
    def __init__(self):
        logger.info("Starting up VectorStoreService...")
        # Load the AI model that turns text into number vectors.
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        # Get the size of the vectors this model creates (e.g., 384).
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index_path = settings.FAISS_INDEX_PATH

        # Load the search index from a file if it exists, otherwise create a new one.
        if os.path.exists(self.index_path):
            logger.info(f"Loading FAISS index from: {self.index_path}")
            self.index = faiss.read_index(self.index_path)
        else:
            logger.info("No FAISS index file found. Creating a new one.")
            # This creates a search index. IndexIDMap lets us use our own integer IDs.
            self.index = faiss.IndexIDMap(faiss.IndexFlatL2(self.dimension))
        logger.info("VectorStoreService is ready.")

    def add_document(self, doc_id: int, content: str):
        """Turns a document's content into a vector and adds it to the index."""
        # The model expects a list of texts, even if it's just one.
        vector = self.model.encode([content])
        # The index needs the IDs in a numpy array.
        ids_to_add = np.array([doc_id])
        # Add the vector and its corresponding ID to the index.
        self.index.add_with_ids(vector, ids_to_add)
        logger.info(f"Added doc with faiss_id {doc_id} to index. Total docs in index: {self.index.ntotal}")

    def search(self, query: str, k: int = 3) -> list[int]:
        """Searches the index for the 'k' most similar documents to a query."""
        if self.index.ntotal == 0:
            logger.warning("Search called on an empty index.")
            return []

        # Turn the user's question into a vector.
        query_vector = self.model.encode([query])
        # Search the index. It returns the distances and the IDs.
        distances, ids = self.index.search(query_vector, k)
        # We only care about the IDs, so we return them.
        # It returns a list of lists, so we take the first one: ids[0].
        # We also filter out any -1s, which can happen if k > index size.
        return [int(id) for id in ids[0] if id != -1]

    def save_index(self):
        """Saves the index to a file so we don't lose it when the app stops."""
        logger.info(f"Saving FAISS index to: {self.index_path}")
        faiss.write_index(self.index, self.index_path)
        logger.info("Index saved.")

# Create one instance of this service for the whole app.
# This way, the big AI model is only loaded into memory once when the app starts.
vector_store_service = VectorStoreService()