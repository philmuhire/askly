"""Tunable settings for the chat / RAG pipeline (override via environment)."""
import os

MAX_TURNS = int(os.getenv("AGENT_MAX_TURNS", "6"))
HISTORY_LIMIT = int(os.getenv("CHAT_HISTORY_LIMIT", "12"))

RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "6"))
# cosine similarity = 1 - cosine distance. Calibrate against YOUR embedding model.
RETRIEVAL_MIN_SIMILARITY = float(os.getenv("RETRIEVAL_MIN_SIMILARITY", "0.30"))
RETRIEVAL_MAX_PER_DOCUMENT = int(os.getenv("RETRIEVAL_MAX_PER_DOCUMENT", "2"))