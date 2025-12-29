from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.services.search_service import search_similar_chunks
from app.services.chat_service import generate_answer
from app.services.conversation_service import (
    create_conversation,
    get_conversation,
    add_message,
    get_latest_conversation,
    list_conversations,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str
    top_k: int = 5
    conversation_id: Optional[str] = None


@router.post("")
def chat(request: ChatRequest):
    # 1. Create or reuse conversation
    conversation_id = request.conversation_id
    if not conversation_id:
        conversation_id = create_conversation()

    # 2. Load previous messages
    convo = get_conversation(conversation_id)
    previous_messages = convo["messages"]

    # 3. Vector search
    search_results = search_similar_chunks(
        request.question,
        top_k=request.top_k,
    )

    context_chunks = [r["text"] for r in search_results]

    # 4. Generate answer
    answer = generate_answer(
        question=request.question,
        context_chunks=context_chunks,
    )

    # 5. Store messages
    add_message(conversation_id, "user", request.question)
    add_message(conversation_id, "assistant", answer)

    # 6. Return response
    return {
        "conversation_id": conversation_id,
        "question": request.question,
        "answer": answer,
        "chunks_used": len(context_chunks),
    }


@router.get("/latest")
def get_latest_chat():
    conversation = get_latest_conversation()

    if not conversation:
        return {
            "conversation_id": None,
            "messages": []
        }

    return {
        "conversation_id": conversation["conversation_id"],
        "messages": conversation["messages"][-10:],  # last 10 messages
    }


@router.get("/conversations")
def get_conversations():
    convs = list_conversations()
    return [
        {
            "conversation_id": str(c["conversation_id"]),
            "title": c.get("title", "New chat"),
        }
        for c in convs
    ]


@router.get("/{conversation_id}")
def get_conversation_messages(conversation_id: str):
    convo = get_conversation(conversation_id)

    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "conversation_id": convo["conversation_id"],
        "messages": convo["messages"],
    }

