from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from app.core.errors import file_not_found
from app.services.search_service import search_similar_chunks
from app.services.chat_service import (
    rewrite_query,
    generate_answer,
)
from app.services.conversation_service import (
    create_conversation,
    get_conversation,
    add_message,
    get_latest_conversation,
    list_conversations,
    rename_conversation_by_id,
    delete_conversation_by_id,
)
from app.services.report_generator import generate_report_pdf

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

    # 3. Rewrite query
    #rewritten_query = rewrite_query(
    #    request.question,
    #    previous_messages
    #)

    # 4. Vector search using rewritten query
    search_results = search_similar_chunks(
        request.question,
        #rewritten_query,
        top_k=request.top_k,
    )
    context_chunks = [r["text"] for r in search_results]

    # 5. Generate answer using rewritten query
    answer = generate_answer(
        question=request.question,
        #question=rewritten_query,
        previous_messages=previous_messages,
        context_chunks=context_chunks,
    )

    # 6. Store new messages
    #rewrite = rewritten_query if rewritten_query != request.question else None
    #add_message(conversation_id, "user", request.question, rewrite)
    add_message(conversation_id, "user", request.question)
    add_message(conversation_id, "assistant", answer)

    # 7. Return response
    return {
        "conversation_id": conversation_id,
        "question": request.question,
        #"rewrite": rewrite,
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
        raise file_not_found("Conversation not found")

    return {
        "conversation_id": convo["conversation_id"],
        "messages": convo["messages"],
    }


@router.patch("/{conversation_id}/rename")
async def rename_conversation(conversation_id: str, new_title: str):
    result = rename_conversation_by_id(conversation_id, new_title)

    if result.matched_count == 0:
        raise file_not_found("Conversation not found")
    
    return {"conversation_id": conversation_id, "title": new_title}


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    result = delete_conversation_by_id(conversation_id)

    if result.deleted_count == 0:
        raise file_not_found("Conversation not found")

    return {"deleted": True}


@router.get("/{conversation_id}/report")
def generate_report(conversation_id: str):
    conversation = get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    output_path = f"reports/{conversation_id}.pdf"
    generate_report_pdf(conversation, output_path)

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename="conversation_report.pdf",
    )
