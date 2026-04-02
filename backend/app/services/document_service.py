import os
import shutil
import tempfile
import uuid
from time import perf_counter
from fastapi import UploadFile
from sqlalchemy.orm import Session
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_core.documents import Document as LangchainDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_ollama import OllamaEmbeddings
from app.db.postgres import SessionLocal
from app.db.chroma import get_chroma_collection
from app.models.document import Document
from app.core.config import settings
from app.core.logger import logger

def get_embeddings_model():
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=settings.GEMINI_API_KEY
    #  return OllamaEmbeddings(
    #     base_url=settings.OLLAMA_BASE_URL,
    #     model=settings.EMBEDDING_MODEL
    )

   

def parse_file(file_path: str, file_type: str) -> list[LangchainDocument]:
    if file_type == "pdf":
        loader = PyPDFLoader(file_path)
    elif file_type == "docx":
        loader = Docx2txtLoader(file_path)
    elif file_type == "txt":
        loader = TextLoader(file_path, encoding='utf-8')
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    return loader.load()

def ingest_document(doc_id: uuid.UUID, file_path: str, file_type: str, filename: str):
    start_time = perf_counter()
    db = SessionLocal()
    try:
        if file_type == "text_input":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            docs = [LangchainDocument(page_content=content)]
        else:
            docs = parse_file(file_path, file_type)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=75
        )
        chunks = splitter.split_documents(docs)
        
        if not chunks:
            raise ValueError("No text could be extracted or chunked from the document.")

        collection = get_chroma_collection()
        embeddings_model = get_embeddings_model()
        
        texts = [chunk.page_content for chunk in chunks]
        metadatas = []
        ids = []

        for i, chunk in enumerate(chunks):
            meta = {
                "doc_id": str(doc_id),
                "filename": filename,
                "chunk_index": i,
                "source_type": file_type
            }
            metadatas.append(meta)
            ids.append(f"{doc_id}_chunk_{i}")

        embeddings = embeddings_model.embed_documents(texts)
        
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts
        )

        db_doc = db.query(Document).filter(Document.id == doc_id).first()
        if db_doc:
            db_doc.status = "ready"
            db_doc.chunk_count = len(chunks)
            db.commit()

        elapsed_ms = (perf_counter() - start_time) * 1000
        logger.info("DOC_INGESTED", extra={
            "doc_id": str(doc_id),
            "doc_filename": filename,
            "chunk_count": len(chunks),
            "latency_ms": elapsed_ms,
            "status": "ready"
        })

    except Exception as e:
        logger.error(f"Error ingesting document {doc_id}: {e}")
        db.rollback()
        db_doc = db.query(Document).filter(Document.id == doc_id).first()
        if db_doc:
            db_doc.status = "failed"
            db.commit()
            
        elapsed_ms = (perf_counter() - start_time) * 1000
        logger.info("DOC_INGESTED", extra={
            "doc_id": str(doc_id),
            "doc_filename": filename,
            "chunk_count": 0,
            "latency_ms": elapsed_ms,
            "status": "failed"
        })
    finally:
        db.close()
        # Clean up temp file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Failed to remove temp file {file_path}: {e}")

def save_temp_file(upload_file: UploadFile) -> str:
    fd, path = tempfile.mkstemp(suffix=f"_{upload_file.filename}")
    with os.fdopen(fd, 'wb') as f:
        shutil.copyfileobj(upload_file.file, f)
    return path

def save_text_to_temp_file(text: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(text)
    return path
