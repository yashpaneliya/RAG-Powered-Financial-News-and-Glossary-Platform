from pinecone import Pinecone
import os
from core.logger import logger

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINCONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

try:
    logger.info("Initializing Pinecone connection...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    logger.info("Pinecone connected!")
except Exception as e:
    logger.error("Pinecone connection failed!!")

def get_glossary_index():
    if PINECONE_INDEX_NAME not in pc.list_indexes():
        logger.warning(f"Index {PINECONE_INDEX_NAME} not found. Creating it...")
        pc.create_index(PINECONE_INDEX_NAME, dimension=1536, metric="cosine")

    index = pc.Index(PINECONE_INDEX_NAME)
    logger.info(f"Connected to pinecone index {PINECONE_INDEX_NAME}")
    return index