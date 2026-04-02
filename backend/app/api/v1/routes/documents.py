from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.postgres import get_db
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentListResponse, TextInputRequest
from app.core.dependencies import require_admin
from app.core.exceptions import ValidationError, NotFoundError
from app.services.document_service import ingest_document, save_temp_file, save_text_to_temp_file
from app.db.chroma import get_chroma_collection

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_MIME_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
]

@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    total = db.query(Document).count()
    items = db.query(Document).order_by(Document.created_at.desc()).offset(offset).limit(limit).all()
    pages = (total + limit - 1) // limit
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if file.size and file.size > 10 * 1024 * 1024:
        raise ValidationError("File size must not exceed 10MB.")
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError("Unsupported file type. Use .pdf, .docx, or .txt.")
        
    if file.content_type == "application/pdf":
        file_type = "pdf"
    elif "wordprocessingml" in file.content_type:
        file_type = "docx"
    else:
        file_type = "txt"

    file_path = save_temp_file(file)
    
    doc = Document(
        filename=file.filename,
        file_type=file_type,
        file_size_bytes=file.size,
        status="processing",
        uploaded_by=current_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    background_tasks.add_task(ingest_document, doc.id, file_path, file_type, file.filename)
    
    return {"document_id": doc.id, "status": "processing"}

@router.post("/text", status_code=status.HTTP_202_ACCEPTED)
async def add_text_document(
    body: TextInputRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    file_path = save_text_to_temp_file(body.text)
    
    doc = Document(
        filename=body.filename,
        file_type="text_input",
        file_size_bytes=len(body.text.encode('utf-8')),
        status="processing",
        uploaded_by=current_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    background_tasks.add_task(ingest_document, doc.id, file_path, "text_input", body.filename)
    
    return {"document_id": doc.id, "status": "processing"}

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: UUID, 
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise NotFoundError("Document not found.")
        
    # Delete chunks from ChromaDB
    collection = get_chroma_collection()
    results = collection.get(where={"doc_id": str(doc_id)})
    if results and results.get("ids"):
        collection.delete(ids=results["ids"])
    
    # Delete from DB
    db.delete(doc)
    db.commit()
    
    return {"message": "Document deleted successfully."}
