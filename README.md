RAG-Based AI-Powered FAQ System
A FastAPI backend implementing Retrieval-Augmented Generation (RAG) to answer user queries using your own document collection. This project supports document ingestion, vector indexing, semantic search, and AI-powered answering using LLMs.

Features
REST API with FastAPI

Document storage in MongoDB

Vector search with FAISS

Embeddings via Sentence Transformers or OpenAI

LLM-powered answer generation (OpenAI GPT, etc.)

Structured logging and error handling


Endpoints
Method	Endpoint	Description
POST	/documents/	Upload a document
GET	/documents/	List all stored documents
POST	/query/	Query the AI-powered FAQ system
GET	/health/	Health check endpoint


Getting Started
1. Clone the Repository
git clone https://github.com/damodarpurohit29/RAG_FAQ.git
cd rag-faq-system
2. Set Up Environment
Python 3.11+ recommended.

Install dependencies:
pip install -r requirements.txt


3. Configure Environment Variables
Create a .env file in the root directory:

text
DATABASE_URL=mongodb+srv://<username>:<password>@<cluster-url>/<dbname>
DATABASE_NAME=faq_db
OPENAI_API_KEY=your-openai-api-key
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
FAISS_INDEX_PATH=faiss_index.bin


4. Run the Application

uvicorn app.main:app --reload