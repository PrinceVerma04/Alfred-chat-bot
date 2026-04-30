"""Project configuration for the Alfred Lab chatbot."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Company Configuration
COMPANY_URL = "https://alfred-lab.in/"
COMPANY_NAME = "Alfred Lab"
CONTACT_PHONE = "+81 53-525-8422"
CONTACT_EMAIL = "info.india@alfred-lab.in"
CONTACT_HOURS = "9:00-18:00, excluding Sundays and public holidays"

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY and OPENAI_API_KEY and OPENAI_API_KEY.startswith("gsk_"):
    GROQ_API_KEY = OPENAI_API_KEY
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Embedding Configuration
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local").lower()
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
LOCAL_EMBEDDING_DIMENSIONS = int(os.getenv("LOCAL_EMBEDDING_DIMENSIONS", "384"))

# Vector Store Configuration
DATA_DIR = BASE_DIR / "data"
FAISS_INDEX_PATH = DATA_DIR / "faiss_index"
SCRAPED_DATA_PATH = DATA_DIR / "scraped_pages.json"
SESSION_REQUESTS_PATH = DATA_DIR / "session_requests.json"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 200

# Scraper Configuration
MAX_PAGES = int(os.getenv("MAX_SCRAPE_PAGES", "20"))

# Chat Configuration
CONVERSATION_HISTORY_SIZE = 10
