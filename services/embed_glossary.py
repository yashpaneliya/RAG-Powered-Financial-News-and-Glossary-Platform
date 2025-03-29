from core.database import get_db
from core.logger import logger
from models.glossary import GlossaryTerm
from services.embedding_service import store_embeddings_pinecone

def embed_and_store_glossary(limit: int = None, offset: int = None, include_ids: list = []):
    """
    Batch process: Embed all glossary terms and store them in Pinecone.
    """
    logger.info(f"Starting glossary embedding process...")

    db = next(get_db())
    if limit and offset:
        glossary_terms = db.query(GlossaryTerm).limit(limit).offset(offset).all()
    else:
        glossary_terms = db.query(GlossaryTerm).filter(GlossaryTerm.embedded == False).all()
    
    if len(include_ids) > 0:
        extra_terms = db.query(GlossaryTerm).filter(GlossaryTerm.id.in_(include_ids)).all()
        glossary_terms.extend(extra_terms)

    logger.info(f"Fetched {len(glossary_terms)} terms from DB")

    embedded_ids = []
    for term in glossary_terms:
        logger.info(f"Processing term: {term}")
        combined_text = f"{term.term} - {term.definition} - {term.simplified_explanation}"
        store_embeddings_pinecone(str(term.id), combined_text)
        embedded_ids.append(term.id)
    
    logger.info("Glossary batch embedding process completed")
    db.query(GlossaryTerm).filter(GlossaryTerm.id.in_(embedded_ids)).update({GlossaryTerm.embedded: True}, synchronize_session='fetch')
    db.commit() 
    logger.info("Updated embedding status in DB")

if __name__ == "__main__":
    embed_and_store_glossary()