from datetime import datetime
from uuid import uuid4
from app.db.mongodb import db


MAX_MESSAGES = 10  # keep last N messages total


def create_conversation() -> str:
    conversation_id = str(uuid4())
    db.conversations.insert_one({
        "conversation_id": conversation_id,
        "messages": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    })
    return conversation_id


def get_conversation(conversation_id: str) -> list[dict]:
    convo = db.conversations.find_one(
        {"conversation_id": conversation_id},
        {"_id": 0, "messages": 1}
    )
    return convo["messages"] if convo else []


def add_message(conversation_id: str, role: str, content: str):
    db.conversations.update_one(
        {"conversation_id": conversation_id},
        {
            "$push": {
                "messages": {
                    "$each": [{
                        "role": role,
                        "content": content,
                        "timestamp": datetime.utcnow(),
                    }],
                    "$slice": -MAX_MESSAGES,
                }
            },
            "$set": {"updated_at": datetime.utcnow()},
        },
        upsert=True,
    )


def get_latest_conversation():
    return db.conversations.find_one(
        {},
        sort=[("updated_at", -1)]
    )

