from pathlib import Path

# dirs
PROJECT_ROOT = Path(__file__).parent
DATASET_PATH = PROJECT_ROOT / "assets/dataset"
VEC_STORE_PERSIST_PATH = PROJECT_ROOT / "assets/vecdb"
CHECKPOINT_DB_PATH = PROJECT_ROOT / "assets/checkpoints/"

# names
LLM_MODEL = "Qwen/Qwen3-4B-Instruct-2507"
EMBEDDINGS_MODEL = "qwen3-embedding:0.6b"
VEC_STORE_COLLECTION_NAME = "legal_chunks"

DATASET_PATH.mkdir(parents=True, exist_ok=True)
VEC_STORE_PERSIST_PATH.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DB_PATH.mkdir(parents=True, exist_ok=True)


SYSTEM_PROMPT = """
    Document: {document}
    Source : {source}
    Analyze the given document and produce a Title Review Summary with:

    1. Current lien table (lender/amt/status/recording/risk)
    2. Clear elements (taxes, judgments, etc.)
    3. Risks & issues (numbered)
    4. Marketability verdict + conditions
    5. Closing instructions
    6. Key facts extracted
    7. Final recommendation
    8. Add given source as reference

    Format as professional title report. Flag ALL risks.

    Don't make things up. Make your response grounded on the given docuemnt.
    Generate response in markdown format.
"""
