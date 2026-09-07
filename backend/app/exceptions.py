class RAGError(Exception):
    """Base exception for RAG application."""

class DocumentIngestionError(RAGError):
    """Raised when document ingestion fails."""

class EmbeddingError(RAGError):
    """Raised when embedding generation fails."""

class RetrievalError(RAGError):
    """Raised when vector retrieval fails."""

