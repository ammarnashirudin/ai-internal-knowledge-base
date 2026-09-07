import logging

from dataclasses import field
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from google.auth import default
from pydantic import BaseModel, Field

from .rag import (
    ingest_document,
    answer_question,
)

logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger(
    "knowledge-base"
)

app = FastAPI(
    title = "AI Internal Knowledge Base",
    version = "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.1.101:3000",
        "https://ai-internal-knowledge-base-lake.vercel.app",
        "https://ai-internal-knowledge-base-bsu5sdgb3-ammarnashirudins-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IngestRequest(BaseModel):
    source_type: str
    source_id : str
    title: str
    content: str
    metadata: dict = {}

class AskRequest(BaseModel):
    question: str= Field(
        min_length=3
    )
    match_threshold: float = Field(
        default=0.7,
        ge=0,
        le=1,
    )
    match_count: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    department: str|None=None

@app.get("/")
def root():
    return {
        "name" : "AI Internal Knowledge Base",
        "status" : "running",
        "llm" : "Gemini",
        "embedding": "gemini-embedding-001",
    }

@app.get("/health")
def health():
    return{
        "status": "ok",
        "service" : "ai-internal-knowledge-base",
        "version" : "1.0.0",
    }

@app.post("/ingest")
def ingest(request: IngestRequest):

    logger.info(
        "Ingestion started: source_id=%s",
        request.source_id,
    )
    try:
        result = ingest_document(
            source_type=request.source_type,
            source_id=request.source_id,
            title=request.title,
            content=request.content,
            metadata=request.metadata
        )

        logger.info(
            "ingestion completed: source_id=%s status=%s",
            request.source_id,
            result.get("status")
        )

        return result
    
    except Exception as e:

        logger.exception(
            "Ingestion failed: source_id=%s",
            request.source_id,
        )

        raise HTTPException(
            status_code=500, 
            detail={
                "error": "INGESTION_FAILED",
                "message" : str(e),
            },
            )

@app.post("/ask")
def ask(request: AskRequest):
    logger.info(
        "RAG quey started"
    )
    try:
        result = answer_question(
            question=request.question,
            match_threshold=request.match_threshold,
            match_count=request.match_count,
            department=request.department,
        )

        logger.info(
            "RAG query completed: status =%s",
            result.get(
                "retrieval",
                {}
            ).get("status")
        )
        return result
        
    except Exception as e:
        logger.exception(
            "RAG query failed"
        )
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "RAG_QUERY_FAILED",
                "message" : str(e)
            },
        )