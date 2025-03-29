from pinecone import Pinecone, ServerlessSpec
import os
from core.logger import logger

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINCONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

logger.info(f"Picone ENV config: {PINECONE_ENVIRONMENT} | {PINECONE_INDEX_NAME}")

spec = ServerlessSpec(
    cloud='aws',
    region=PINECONE_ENVIRONMENT
)

try:
    logger.info("Initializing Pinecone connection...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    logger.info("Pinecone connected!")
except Exception as e:
    logger.error("Pinecone connection failed!!")

def get_glossary_index():
    indexes = pc.list_indexes()
    index_names = [index['name'] for index in indexes]
    logger.info(f"List of pinecone indexes: {index_names}")

    if PINECONE_INDEX_NAME not in index_names:
        logger.warning(f"Index {PINECONE_INDEX_NAME} not found. Creating it...")
        pc.create_index(PINECONE_INDEX_NAME, dimension=1536, metric="cosine", spec=spec)

    index = pc.Index(PINECONE_INDEX_NAME)
    logger.info(f"Connected to pinecone index {PINECONE_INDEX_NAME}")
    return index