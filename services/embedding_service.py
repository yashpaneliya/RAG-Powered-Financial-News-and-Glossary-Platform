import openai
import os
from core.logger import logger
from core.pinecone_client import get_glossary_index

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

index = get_glossary_index()

def generate_embedding(text: str) -> list:
    try:
        logger.info(f"Generating embedding for text: {text[:50]}...")
        response = openai.embeddings.create(
            input=[text],
            model="text-embedding-ada-002"
        )
        embeddings = response.data[0].embedding
        logger.info(f"Embeddings generated: {len(embeddings)} dimensions")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {str(e)}")
        return []

def store_embeddings_pinecone(id: str, text: str):
    try:
        embeddings = generate_embedding(text)
        if not embeddings:
            logger.error(f"Failed to generate embeddings for {id}")
            return
        
        logger.info(f"Storing embedding for ID {id} in Pinecone...")
        index.upsert(vectors=[(id, embeddings)])
        logger.info(f"Embedding stored successfully for ID {id}.")
    except Exception as e:
        logger.error(f"Failed to store embedding in Pinecone: {str(e)}")