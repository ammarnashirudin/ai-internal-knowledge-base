import time
from .utils import generate_content_hash
from langchain_google_genai import ChatGoogleGenerativeAI

from .config import(
    GOOGLE_API_KEY,
    LLM_MODEL,
)

from .embeddings import (
    embed_documents_safe,
    embed_query_safe,
)
from .chunking import split_document
from .retrieval import (
    supabase,
    similarity_search,
)

llm = ChatGoogleGenerativeAI(
    model=LLM_MODEL,
    temperature=0,
    google_api_key=GOOGLE_API_KEY,
)

SYSTEM_PROMPT = """
You are an internal company knowledge assistant.

Your job is to answer questions using ONLY
the provided company knowledge base context.

STRICT RULES:

1. Never invent facts.
2. Never use outside knowledge.
3. If the context does not contain enough
   information to answer the question,
   explicitly say that the information
   was not found in the knowledge base.
4. Do not infer specific policy thresholds
   that are not explicitly stated.
5. If the context says something about a
   different threshold, do not assume it
   applies to the user's threshold.
6. Prefer exact information from the context.
7. Keep answers concise and factual.
8. Answer in the same language as the user.
9. Do not claim a policy exists unless it
   appears in the context.
10. Do not combine unrelated sources unless
    the context clearly supports doing so.

Context:

{context}

Question:

{question}
"""
MAX_DOCUMENT_LENGTH = 100_000

def validate_document(
        title: str,
        content: str,
):
    if not title.strip():
        raise ValueError(
            "Document title cannot be empty"
        )
    if not content.strip():
        raise ValueError(
            "Document content cannot be empty"
        )
    if len(content)<20:
        raise ValueError(
            "Document content is too short"
        )
    if len(content)>MAX_DOCUMENT_LENGTH:
        raise ValueError(
            "Document exceeds maximum allowed size"
        )

def log_ingestion(
        source_type: str,
        source_id: str,
        status: str,
        document_id: str | None=None,
        version: int | None=None,
        chunks_created: int = 0,
        error_message: str | None=None,
):
    supabase.table(
        "ingestion_logs"
    ).insert(
        {
            "source_type" : source_type,
            "source_id" : source_id,
            "status" : status,
            "document_id" : document_id,
            "version" : version,
            "chunks_created" : chunks_created,
            "error_message" : error_message,
        }
    ).execute()

def ingest_document(
    source_type: str,
    source_id: str,
    title: str,
    content: str,
    metadata: dict | None = None,
):

    try:

        # Validation

        validate_document(
            title=title,
            content=content,
        )

        metadata = metadata or {}

        # Generate content hash

        content_hash = generate_content_hash(content)

        # Check existing document

        existing_response = (
            supabase
            .table("documents")
            .select("id, content_hash, version")
            .eq("source_type", source_type)
            .eq("source_id", source_id)
            .limit(1)
            .execute()
        )

        # Document unchanged

        if existing_response.data:

            existing = existing_response.data[0]

            if existing["content_hash"] == content_hash:

                log_ingestion(
                    source_type=source_type,
                    source_id=source_id,
                    status="unchanged",
                    document_id=existing["id"],
                    version=existing["version"],
                    chunks_created=0,
                )

                return {
                    "status": "unchanged",
                    "document_id": existing["id"],
                    "version": existing["version"],
                    "chunks_created": 0,
                }

        # Determine version

        if existing_response.data:
            version = existing_response.data[0]["version"] + 1
        else:
            version = 1

        # Upsert document

        response = (
            supabase
            .table("documents")
            .upsert(
                {
                    "source_type": source_type,
                    "source_id": source_id,
                    "title": title,
                    "content": content,
                    "metadata": metadata,
                    "content_hash": content_hash,
                    "version": version,
                },
                on_conflict="source_type, source_id",
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Failed to ingest document"
            )

        document = response.data[0]
        document_id = document["id"]

        # Delete old chunks

        (
            supabase
            .table("document_chunks")
            .delete()
            .eq("document_id", document_id)
            .execute()
        )

        # Chunk document

        chunks = split_document(content)

        # Generate Gemini embeddings

        vectors = embed_documents_safe(chunks)

        # Prepare database rows

        rows = []

        for index, (chunk, vector) in enumerate(
            zip(chunks, vectors)
        ):
            rows.append(
                {
                    "document_id": document_id,
                    "chunk_index": index,
                    "content": chunk,
                    "embedding": vector,
                    "metadata": {
                        **metadata,
                        "title": title,
                        "source_id": source_id,
                        "version": version,
                    },
                }
            )

        # Insert vectors

        if rows:
            (
                supabase
                .table("document_chunks")
                .insert(rows)
                .execute()
            )

        # Log successful ingestion

        log_ingestion(
            source_type=source_type,
            source_id=source_id,
            status="indexed",
            document_id=document_id,
            version=version,
            chunks_created=len(rows),
        )

        return {
            "status": "indexed",
            "document_id": document_id,
            "version": version,
            "chunks_created": len(rows),
        }

    except Exception as e:

        log_ingestion(
            source_type=source_type,
            source_id=source_id,
            status="failed",
            error_message=str(e),
        )

        raise
    
def answer_question(
    question: str,
    match_threshold: float = 0.50,
    match_count: int = 5,
    department : str | None = None,
):
    # embed question using gemini

    start_embedding = time.perf_counter()

    query_embedding = embed_query_safe(question)

    embedding_time = time.perf_counter() - start_embedding
    print(f"[TIMING] Query embedding: {embedding_time:.3f}s")

    # semantic search

    start_retrieval = time.perf_counter()

    chunks = similarity_search(
        query_embedding=query_embedding,
        match_threshold=match_threshold,
        match_count=match_count,
        department=department,
    )

    retrieval_time = time.perf_counter() - start_retrieval
    print(f"[TIMING] Retrieval: {retrieval_time:.3f}s")

    # Nothing found

    if not chunks:
        return {
            "answer" : (
                "information not found in the knowledge base"
            ),
            "sources": [],
        }
    
    best_similarity = max(
        chunk["similarity"]
        for chunk in chunks
    )

    # Determine retrieval confidence level
    if best_similarity >= 0.75:
        confidence_status = "high_confidence"

    elif best_similarity >= 0.65:
        confidence_status = "medium_confidence"

    else:
        confidence_status = "low_confidence"


    # Reject only low-confidence retrieval
    if confidence_status == "low_confidence":
        return {
            "answer": (
                "Information not found in the knowledge base."
            ),
            "sources": [],
            "retrieval": {
                "status": confidence_status,
                "best_similarity": round(
                    best_similarity,
                    4
                ),
                "chunks_retrieved": len(chunks),
            },
        }

    # Build context
    context_parts = []

    for index, chunk in enumerate(
        chunks, start=1
    ):
        
        metadata = chunk.get("metadata") or {}

        title = metadata.get(
            "title",
            "Unknown Source"
        )

        context_parts.append(
            f"[Source{index}]\n"
            f"Title: {title}\n"
            f"{chunk['content']}\n"
        )

    context = "\n\n".join(context_parts)

    # Generate answer with Gemini LLM

    prompt = SYSTEM_PROMPT.format(
        context=context,
        question=question,
    )

    start_generation = time.perf_counter()

    response = llm.invoke(prompt)

    generation_time = time.perf_counter() - start_generation
    print(f"[TIMING] Gemini generation: {generation_time:.3f}s")
    
    # Sources

    sources = []
    for chunk in chunks:
        metadata = chunk.get("metadata") or {}
        sources.append(
            {
                "document_id": chunk["document_id"],
                "title": metadata.get("title", "Unknown Source"),
                "department": metadata.get("department"),
                "category": metadata.get("category"),
                "version": metadata.get("version"),
                "similarity": round(chunk["similarity"],4)
            }
        )

    answer = response.content

    if isinstance(answer, list):
        answer = "".join(
            item.get("text","")
            for item in answer
            if isinstance(item, dict)
        )

    if any(
        phrase in answer.lower()
        for phrase in [
            "information not found",
            "not found in the knowledge base",
            "does mot contain",
            "not available"
            "tidak ditemukan",
            "tidak tersedia",
        ]
    ):
        return {
            "answer": answer,
            "sources": [],
            "retrieval": {
                "status": confidence_status,
                "best_similarity": round(
                    best_similarity,
                    4,
                ),
                "chunks_retrieved": len(chunks),
            },
        }

    return{
        "answer" : answer,
        "sources" : sources,
        "retrieval" : {
            "status" : confidence_status,
            "best_similarity" : round(
                best_similarity,
                4,
            ),
            "chunks_retrieved" : len(chunks),
        },
    }