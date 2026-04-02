import uuid
from time import perf_counter
from app.db.chroma import get_chroma_collection
from app.services.document_service import get_embeddings_model
from app.models.message import Message
from sqlalchemy.orm import Session
from app.core.config import settings

def retrieve(query: str, top_k: int = 4, threshold: float = 0.45) -> tuple[list[str], list[dict], float, str]:
    embeddings_model = get_embeddings_model()
    query_vector = embeddings_model.embed_query(query)
    
    collection = get_chroma_collection()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )
    
    chunks = []
    sources = []
    best_score = 1.0
    rag_path = "fallback"

    if results.get("distances") and results["distances"][0]:
        best_score = results["distances"][0][0]
        if best_score < threshold:
            rag_path = "rag"
            for i in range(len(results["documents"][0])):
                doc_text = results["documents"][0][i]
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                
                chunks.append(doc_text)
                sources.append({
                    "filename": metadata.get("filename"),
                    "chunk_index": metadata.get("chunk_index"),
                    "doc_id": metadata.get("doc_id"),
                    "score": distance
                })

    return chunks, sources, best_score, rag_path

def build_prompt_with_memory(
    current_query: str,
    session_id: uuid.UUID,
    retrieved_chunks: list[str],
    db: Session,
) -> tuple[list[dict], str]:
    
    history = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(settings.CHAT_MEMORY_TURNS * 2)
        .all()
    )
    if history and history[0].role == "user" and history[0].content == current_query:
        history = history[1:]
        
    history.reverse()

    contents = []
    for msg in history:
        contents.append({
            "role": "user" if msg.role == "user" else "model",
            "parts": [{"text": msg.content}]
        })

    if retrieved_chunks:
        system_instruction = """You are EduChat Pro, an AI assistant for college students.
Your sole purpose is to answer questions based on the knowledge documents provided to you.
Rules:
- Answer ONLY from the provided CONTEXT below.
- If the CONTEXT does not contain the answer, clearly say: "I don't have specific information about that in my knowledge base. Please contact the college office."
- Do NOT make up facts, dates, names, or policies.
- Keep answers concise, clear, and student-friendly.
- Do NOT answer questions unrelated to education or college matters."""

        context_str = "\n\n".join(retrieved_chunks)
        current_text = f"CONTEXT:\n{context_str}\n\nQUESTION:\n{current_query}"
    else:
        system_instruction = """You are EduChat Pro, a general educational AI assistant for college students.
You do not have access to this college's specific documents for this query.
Rules:
- Answer general educational questions helpfully.
- Clearly state that your answer is based on general knowledge, not this institution's data.
- Do NOT answer questions unrelated to education."""

        current_text = current_query

    contents.append({"role": "user", "parts": [{"text": current_text}]})
    return contents, system_instruction
