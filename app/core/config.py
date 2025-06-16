# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

# This class defines all the settings our application needs.
# Pydantic will automatically read them from the .env file.
class Settings(BaseSettings):
    # Tell Pydantic to load settings from a file named ".env"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # The connection link for our MongoDB database
    DATABASE_URL: str
    # The name of our database
    DATABASE_NAME: str = "faq_db"

    # The secret key for the OpenAI API
    OPENAI_API_KEY: str

    # The name of the model we use to create text embeddings (vectors)
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    # Where to save our FAISS vector index file
    FAISS_INDEX_PATH: str = "faiss_index.bin"

# Create one single "settings" object that we can import and use anywhere
# in our app. This is better than loading the .env file everywhere.
settings = Settings()