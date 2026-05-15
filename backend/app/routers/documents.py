import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import DocumentResponse, GenerateResponse, ReviewContent, ReviewChangesContent, StatusResponse
from ..storage import create_document, get_document, get_review, get_changes, save_review, save_changes
from ..utils import is_allowed_file, find_changes, UPLOAD_DIR, MAX_FILE_SIZE
from ..llm_app.test_agent import TestAgent

router = APIRouter(prefix="/api/documents", tags=["documents"])
DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), db: DbDep = None):

    # check if any file provided
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # check if we have the allowed file type
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="File type not allowed. Accepted: .pdf, .png",
        )

    content = await file.read()

    # check if the file crosses file_size limit
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 2MB)")

    # all checks passed, we can save the file in out database
    doc_id = uuid.uuid4().hex[:12]
    file_path = UPLOAD_DIR / doc_id
    file_path.write_bytes(content)

    await create_document(db, doc_id, file.filename, file_path)

    return DocumentResponse(
        document_id=doc_id,
        filename=file.filename,
        uploaded_at=datetime.now(timezone.utc),
    )


@router.post("/{document_id}/generate", response_model=GenerateResponse)
async def generate_review(document_id: str, db: DbDep = None):
    doc = await get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    with open(doc["file_path"], "rb") as file:
        file_bytes = file.read()
    with open(f"/tmp/{document_id}.pdf", "wb") as file:
        file.write(file_bytes)

    review = TestAgent(f"/tmp/{document_id}.pdf").generate_report()

    # review = (
    #     f"# Title Review\n\n"
    #     f"## Document: {doc['filename']}\n\n"
    #     f"### Summary\n\n"
    #     f"This document has been reviewed by the LLM. "
    #     f"The following observations were made:\n\n"
    #     f"- **Clarity**: The document is clearly structured.\n"
    #     f"- **Completeness**: All required sections are present.\n"
    #     f"- **Accuracy**: The information appears consistent.\n\n"
    #     f"### Recommendations\n\n"
    #     f"1. Verify all dates and signatures.\n"
    #     f"2. Ensure proper formatting in the final version.\n"
    #     f"3. Consider adding a summary section at the beginning.\n\n"
    #     f"---\n\n"
    #     f"*Generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*"
    # )
    await save_review(db, document_id, review)

    return GenerateResponse(review=review)


@router.get("/{document_id}/review", response_model=ReviewContent)
async def get_review_endpoint(document_id: str, db: DbDep = None):
    doc = await get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    content = await get_review(db, document_id) or ""
    return ReviewContent(content=content)



@router.put("/{document_id}/review", response_model=StatusResponse)
async def save_review_endpoint(document_id: str, payload: ReviewContent, db: DbDep = None):
    doc = await get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    current_review = await get_review(db, document_id)
    new_review = payload.content
    changed = find_changes(current_content=current_review, new_content=new_review)

    if changed:
        await save_changes(db, document_id, changed)

    await save_review(db, document_id, payload.content)

    return StatusResponse(status="saved")



@router.get("/{document_id}/changes", response_model=ReviewChangesContent)
async def get_changes_endpoint(document_id: str, db: DbDep = None):
    result = await get_changes(db, document_id)

    if not result:
        raise HTTPException(status_code=404, detail="No changes found")

    res = []
    for change in result:
        res.append(change.changes)


    return ReviewChangesContent(content=res)
