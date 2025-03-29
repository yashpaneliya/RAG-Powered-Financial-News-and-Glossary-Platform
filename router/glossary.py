from fastapi import APIRouter
from services.rag_service import retrieve_glossary_rag
from core.logger import logger

router = APIRouter()

@router.get("/search")
def search_glossary(query: str, top_k: int = 5):
    logger.info(f"Received search query: {query}, top_k: {top_k}")

    results = retrieve_glossary_rag(query, top_k)

    if results:
        return {"query": query, "results": results}
    else:
        return {"query": query, "results": [], "message": "No matches found."}