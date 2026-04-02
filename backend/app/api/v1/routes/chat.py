import json
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.postgres import get_db
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.schemas.chat import (
    ChatSessionBase, ChatSessionResponse, SessionListResponse,
    SendMessageRequest, MessageResponse
)
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError, ForbiddenError
from app.services.rag_service import retrieve, build_prompt_with_memory
from app.services.gemini_service import gemini_service
from app.core.logger import logger

router = APIRouter(prefix="/sessions", tags=["chat"])

@router.get("", response_model=SessionListResponse)
async def list_sessions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    total = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).count()
    items = (db.query(ChatSession)
             .filter(ChatSession.user_id == current_user.id)
             .order_by(ChatSession.updated_at.desc())
             .offset(offset)
             .limit(limit)
             .all())
    pages = (total + limit - 1) // limit
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }

@router.post("", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    body: ChatSessionBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = ChatSession(
        user_id=current_user.id,
        title=body.title
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.delete("/{session_id}")
async def delete_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise NotFoundError("Chat session not found.")
    if str(session.user_id) != str(current_user.id):
        raise ForbiddenError("Not authorized to delete this session.")
        
    db.query(Message).filter(Message.session_id == session_id).delete()
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully."}

@router.get("/{session_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session or str(session.user_id) != str(current_user.id):
        raise NotFoundError("Chat session not found.")
        
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    return messages

def save_message(db: Session, session_id: UUID, role: str, content: str, sources: list = None) -> Message:
    msg = Message(
        session_id=session_id,
        role=role,
        content=content,
        sources=sources
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session:
        session.updated_at = msg.created_at
        db.commit()
        
    return msg

@router.post("/{session_id}/messages/stream")
async def send_message_stream(
    session_id: UUID,
    body: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session or str(session.user_id) != str(current_user.id):
        raise NotFoundError("Chat session not found.")

    if session.title == "New Chat":
        new_title = body.content[:30] + ("..." if len(body.content) > 30 else "")
        session.title = new_title
        db.commit()

    save_message(db, session_id, "user", body.content)

    chunks, sources, best_score, rag_path = retrieve(body.content)

    logger.info("RAG_QUERY", extra={
        "user_id": str(current_user.id),
        "session_id": str(session_id),
        "query": body.content,
        "retrieved_chunks": sources,
        "best_score": best_score,
        "rag_path": rag_path
    })

    contents, system_inst = build_prompt_with_memory(body.content, session_id, chunks, db)

    async def token_generator():
        full_response = ""
        try:
            async for token in gemini_service.stream(contents, system_inst):
                full_response += token
                yield f"data: {json.dumps({'token': token})}\n\n"
                
            save_message(db, session_id, "assistant", full_response, sources)
            yield f"data: {json.dumps({'done': True, 'sources': sources})}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(token_generator(), media_type="text/event-stream")
