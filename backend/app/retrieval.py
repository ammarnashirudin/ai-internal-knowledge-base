from supabase import create_client

from .config import (
    SUPABASE_URL,
    SUPABASE_KEY,
)

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)

def similarity_search(
        query_embedding: list[float],
        match_threshold: float = 0.7,
        match_count: int = 5,
        department: str | None = None,
):
    response = supabase.rpc(
        "match_document_chunks",
        {
            "query_embedding": query_embedding,
            "match_threshold": match_threshold,
            "match_count": match_count,
            "filter_department": department,
        },    
    ).execute()

    return response.data  or []