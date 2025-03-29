from core.database import get_db
from core.logger import logger
from core.pinecone_client import get_glossary_index
from models.glossary import GlossaryTerm
from services.embedding_service import generate_embedding

def retrieve_glossary_rag(query: str, top_k: int = 5):
    """
    Perform hybrid RAG retrieval:
    - Generate query embedding
    - Search Pinecone for vector similarity
    - Retrieve metadata from PostgreSQL
    """
    logger.info(f"Performing RAG retrieval for query: {query}")
    
    try:
        query_embedding = generate_embedding(query)

        index = get_glossary_index()
        logger.info(f"Searching pincone for top {top_k} similar vectors...")

        search_results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_values=False
        )

        pincone_ids = [match['id'] for match in search_results['matches']]
        logger.info(f"Found {len(pincone_ids)} matching terms in pincone")

        db = next(get_db())
        glossary_terms = db.query(GlossaryTerm).filter(GlossaryTerm.id.in_(pincone_ids)).all()

        results = []
        for term in glossary_terms:
            results.append({
                "term": term.term,
                "definition": term.definition,
                "simplified_explanation": term.simplified_explanation,
                "contextual_example": term.contextual_examples
            })

        logger.info(f"RAG retrieval completed")
        return results
    
    except Exception as e:
        logger.error(f"Error in retrieval service: {str(e)}")
        return []