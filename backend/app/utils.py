import os
from pathlib import Path
from difflib import ndiff

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/tmp/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".png"}
MAX_FILE_SIZE = 2 * 1024 * 1024


def is_allowed_file(filename: str) -> bool:
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def get_file_path(document_id: str) -> Path:
    return UPLOAD_DIR / document_id

def find_changes(current_content, new_content):

    if current_content == new_content: return False
    
    diffs = ndiff(current_content.splitlines(), new_content.splitlines())

    changes = ""
    for diff in diffs:
        changes += ("\n"+diff) if diff.startswith(("-", "+")) else ""

    return changes
