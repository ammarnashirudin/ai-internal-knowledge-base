# AI Internal Knowledge Base

An end-to-end RAG (Retrieval-Augmented Generation) system for answering questions from internal company documents.

## Overview

This project demonstrates how internal company knowledge can be transformed into an AI-powered knowledge assistant.

Users can ask questions through a Next.js web interface. The system retrieves relevant document chunks from Supabase pgvector and uses Google Gemini to generate grounded answers.

## Architecture

```text
Google Docs / Notion
        │
        ▼
      n8n
        │
        ▼
    FastAPI API
        │
        ├── Query Embedding
        │
        ▼
 Supabase pgvector
        │
        ▼
 Relevant Document Chunks
        │
        ▼
     Gemini LLM
        │
        ▼
 Answer + Sources
        │
        ▼
    Next.js UI