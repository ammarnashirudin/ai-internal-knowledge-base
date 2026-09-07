from langchain_google_genai import GoogleGenerativeAIEmbeddings

from .config import (
    GOOGLE_API_KEY,
    EMBEDDING_MODEL,
)

from .exceptions import EmbeddingError

embeddings = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    google_api_key=GOOGLE_API_KEY,
    output_dimensionality=1536,
)

def embed_documents_safe(
        documents: list[str],
) -> list[list[float]]:
    try:
        return embeddings.embed_documents(
            documents
        )
    except Exception as e:
        raise EmbeddingError(
            f"failed to generate embeddings: {e}"
        ) from e

def embed_query_safe(
        query:str,
)-> list[float]:
    try:
        return embeddings.embed_query(
            query
        )
    except Exception as e:
        raise EmbeddingError(
            f"Failed to embed query:{e}"
        ) from e