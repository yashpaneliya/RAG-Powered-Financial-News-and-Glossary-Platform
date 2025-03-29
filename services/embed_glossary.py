from core.database import get_db
from core.logger import logger
from models.glossary import GlossaryTerm
from services.embedding_service import store_embeddings_pinecone

def embed_and_store_glossary():
    """
    Batch process: Embed all glossary terms and store them in Pinecone.
    """
    logger.info(f"Starting glossary embedding process...")

    db = next(get_db())

    glossary_terms = db.query(GlossaryTerm).all()
    logger.info(f"Fetched {len(glossary_terms)} terms from DB")

    for term in glossary_terms:
        logger.info(f"Processing term: {term}")
        combined_text = f"{term.term} - {term.definition} - {term.simplified_explanation}"
        store_embeddings_pinecone(str(term.id), combined_text)
    
    logger.info("Glossary batch embedding process completed")


if __name__ == "__main__":
    embed_and_store_glossary()