import uuid
from time import perf_counter
from app.db.chroma import get_chroma_collection
from app.services.document_service import get_embeddings_model
from app.models.message import Message
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logger import logger

def retrieve(
    query: str,
    top_k: int = 3,           # reduced: fewer chunks = fewer tokens
    threshold: float = 0.35,  # tightened: only use RAG when chunks are genuinely relevant
    chunk_threshold: float = 0.50,  # per-chunk filter: drop individual weak matches
    max_chunk_chars: int = 600,     # truncate long chunks to cap context size
) -> tuple[list[str], list[dict], float, str]:
    try:
        embeddings_model = get_embeddings_model()
        query_vector = embeddings_model.embed_query(query)

        collection = get_chroma_collection()
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )
    except Exception as e:
        logger.warning(f"RAG retrieval failed (network/embedding error), falling back to LLM-only: {e}")
        return [], [], 1.0, "fallback"
    
    chunks = []
    sources = []
    best_score = 1.0
    rag_path = "fallback"

    if results.get("distances") and results["distances"][0]:
        best_score = results["distances"][0][0]

        # Only use RAG path if the best chunk is genuinely relevant
        if best_score < threshold:
            rag_path = "rag"
            for i in range(len(results["documents"][0])):
                distance = results["distances"][0][i]

                # Skip individual chunks that are too weak (irrelevant)
                if distance >= chunk_threshold:
                    logger.info(f"Skipping chunk {i} with distance {distance:.3f} (above per-chunk threshold)")
                    continue

                doc_text = results["documents"][0][i]
                metadata = results["metadatas"][0][i]

                # Truncate chunk to cap token usage
                if len(doc_text) > max_chunk_chars:
                    doc_text = doc_text[:max_chunk_chars].rsplit(' ', 1)[0] + "..."

                chunks.append(doc_text)
                sources.append({
                    "filename": metadata.get("filename"),
                    "chunk_index": metadata.get("chunk_index"),
                    "doc_id": metadata.get("doc_id"),
                    "score": round(distance, 4)
                })

        else:
            logger.info(f"Query below relevance threshold (best_score={best_score:.3f}), using fallback path.")

    return chunks, sources, best_score, rag_path

def build_prompt_with_memory(
    current_query: str,
    session_id: uuid.UUID,
    retrieved_chunks: list[str],
    db: Session,
) -> tuple[list[dict], str]:
    
    # Cap history to 3 turns (6 messages) max to control context size
    max_history_messages = min(settings.CHAT_MEMORY_TURNS, 3) * 2
    history = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(max_history_messages)
        .all()
    )
    if history and history[0].role == "user" and history[0].content == current_query:
        history = history[1:]
        
    history.reverse()

    contents = []
    for msg in history:
        # Trim long history messages to avoid bloating context (esp. long assistant answers)
        text = msg.content
        if len(text) > 300:
            text = text[:300].rsplit(' ', 1)[0] + "..."
        contents.append({
            "role": "user" if msg.role == "user" else "model",
            "parts": [{"text": text}]
        })

    if retrieved_chunks:
        system_instruction = """You are EduChat, an intelligent AI assistant for college students.
You have been given CONTEXT excerpts from the college's official knowledge base.

Your job is to ACT AS A HELPFUL ADVISOR — not a document reader.
Use the CONTEXT as your source of truth, but reason over it to genuinely help the student.

Guidelines:
- Understand what the student is ACTUALLY trying to achieve, not just what they literally asked.
- Synthesize and explain the relevant information in your own words — do NOT copy-paste chunks.
- If the student asks to elaborate, go deeper: break it down step by step, give examples, explain implications.
- Connect related pieces of information from the context to give a complete picture.
- Use a clear, friendly, student-oriented tone. Use bullet points, numbered steps, or tables where helpful.
- If the context is partial or unclear, say what you do know and flag what is uncertain.
- Only say "I don't have information on that" if the topic is genuinely absent from the context.
- Do NOT invent facts (names, dates, policies) that are not in the context.
- Stay focused on educational and college-related matters."""

        context_str = "\n\n---\n\n".join(retrieved_chunks)
        current_text = f"KNOWLEDGE BASE CONTEXT:\n{context_str}\n\nSTUDENT QUESTION:\n{current_query}"
    else:
        system_instruction = """You are EduChat, a knowledgeable and friendly AI assistant for college students.
You don't have specific documents for this query, so you are answering from general knowledge.

Guidelines:
- Be genuinely helpful — reason through the question, don't just state facts.
- Explain concepts clearly with examples or steps where relevant.
- If the student asks to elaborate or go deeper, do so thoughtfully.
- Make it explicit when your answer is based on general knowledge vs. institution-specific information.
- Stay focused on education, academic life, and college-related topics."""

        current_text = current_query

    contents.append({"role": "user", "parts": [{"text": current_text}]})
    return contents, system_instruction
