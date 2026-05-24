import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

DATA_DIR = PROJECT_ROOT / "data"
KNOWLEDGEBASE_DIR = DATA_DIR / "knowledgebases"
CHROMA_DIR = DATA_DIR / "chroma"
DB_DIR = DATA_DIR / "db"

CHROMA_COLLECTION_NAME = "knowledge_base"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

DEFAULT_MODEL = "gpt-3.5-turbo"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(KNOWLEDGEBASE_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)