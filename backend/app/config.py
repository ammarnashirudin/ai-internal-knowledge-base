import os

from dotenv import load_dotenv

load_dotenv()


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "gemini-embedding-001"
)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "gemini-2.5-flash"
)


if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY belum diset"
    )

if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL belum diset"
    )

if not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_KEY belum diset"
    )