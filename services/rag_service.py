from collections import defaultdict
from core.database import get_db
from core.logger import logger
from core.pinecone_client import get_glossary_index
from models.glossary import GlossaryTerm
from services.embedding_service import generate_embedding
from utils.nlp_preprocessors import keyword_extraction, preprocess_user_query
import numpy as np

def filter_sql(query: str):
    """
    SQL Filtering with Query Expansion:
    - Tokenizes the query & Removes stopwords
    - Searches for individual keywords in PostgreSQL
    """

    db = next(get_db())
    keywords = keyword_extraction(query)

    if not keywords:
        logger.warning("No valid keywords found in user query")
        return []
    
    logger.info(f"Performing SQL filtering for keywords: {keywords}")

    db_query = db.query(GlossaryTerm).filter(GlossaryTerm.deleted_at == None)

    keyword_filters = [
        (GlossaryTerm.term.ilike(f"%{kw}%"))
        for kw in keywords
    ]

    # Combine filters with OR logic
    final_filter = keyword_filters[0]
    for keyword_filter in keyword_filters[1:]:
        final_filter |= keyword_filter

    db_query = db_query.filter(final_filter)

    filtered_terms = db_query.all()

    logger.info(f"Filtered {len(filtered_terms)} terms using expanded SQL filtering")
    return filtered_terms

def rerank_results(results: list, query_embeddings: list, sql_boost: float = 0.95):
    """
    Reranks the RAG results with hybrid scoring:
    - SQL-filtered results get a boost
    - Cosine score for Pinecone results
    """
    logger.info("Starting reranking with SQL & Exact Match Boosting...")
    if not results:
        logger.warning("No results to rerank.")
        return []

    reranked_results = []
    for result in results:
        term = result['term']
        definition = result['definition']

        candidate_text = f"{term}"
        candidate_text_embeddings = generate_embedding(candidate_text)

        # cosine similarity
        cos_score = np.dot(query_embeddings, candidate_text_embeddings) / (
            np.linalg.norm(query_embeddings) * np.linalg.norm(candidate_text_embeddings)
        )

        base_score = cos_score
        # SQL boost
        if result.get('from_sql', False):
            base_score *= sql_boost
        else:
            base_score = result.get('cos_score', 1)
        
        reranked_results.append({
            "term": result['term'],
            "definition": result['definition'],
            "simplified_explanation": result['simplified_explanation'],
            "contextual_example": result['contextual_example'],
            "from_sql": result.get('from_sql', False),
            "score": base_score
        })

    # Sort results by score
    reranked_results.sort(key=lambda x: x['score'], reverse=True)
    logger.info("Reranking completed with OpenAI embeddings.")
    return reranked_results

def retrieve_glossary_rag(query: str, top_k: int = 5):
    """
    Optimized Hybrid RAG retrieval:
    - SQL filtering with query expansion
    - Pinecone vector search with filtered IDs
    - LLM-based reranking
    """
    logger.info(f"Performing RAG retrieval for query: {query}")
    
    try:
        # SQL Filtering with Query Expansion
        filtered_terms = filter_sql(query)
        filtered_ids = [str(term.id) for term in filtered_terms]
        logger.info(f"Filtered ids to search in Pinecone: {filtered_ids}")
        if not filtered_terms:
            logger.warning("No matching terms found in SQL filtering.")
        
        # Pinecone Vector Retrieval (with filtered IDs)
        query_embedding = generate_embedding(query)

        index = get_glossary_index()
        logger.info(f"Searching pincone for top {top_k} similar vectors...")

        search_results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_values=False,
            include_scores=True
        )

        logger.info(f"Found {len(search_results['matches'])} matching terms in pincone")
        pincone_ids = [match['id'] for match in search_results['matches']]
        pincone_scores = [match['score'] for match in search_results['matches']]
        pinecone_id_score = defaultdict(float)
        for i, id in enumerate(pincone_ids):
            pinecone_id_score[id] = pincone_scores[i]

        db = next(get_db())
        glossary_terms = db.query(GlossaryTerm).filter(GlossaryTerm.id.in_(pincone_ids)).all()

        results = []
        # Combine SQL + Pinecone Results
        # Add SQL terms to results with `from_sql=True`
        for term in filtered_terms:
            results.append({
                "term": term.term,
                "definition": term.definition,
                "simplified_explanation": term.simplified_explanation,
                "contextual_example": term.contextual_examples,
                "from_sql": True  # Flag for SQL-boosted terms
            })
        
        # Add Pinecone terms with `from_sql=False`
        for i, term in enumerate(glossary_terms):
            # Prevent duplicates (SQL + Pinecone)
            if not any(res['term'] == term.term for res in results):
                results.append({
                    "term": term.term,
                    "definition": term.definition,
                    "simplified_explanation": term.simplified_explanation,
                    "contextual_example": term.contextual_examples,
                    "from_sql": False,  # Non-SQL terms
                    "cos_score": pinecone_id_score[str(term.id)]
                })

        # Reranking
        logger.info("Reranking results...")
        reranked_results = rerank_results(results, query_embedding)
        logger.info(f"RAG retrieval with reranking completed")
        return reranked_results
    except Exception as e:
        logger.error(f"Error in retrieval service: {str(e)}")
        return []