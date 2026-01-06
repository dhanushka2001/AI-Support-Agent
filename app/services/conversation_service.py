from fastapi import HTTPException
from datetime import datetime
from uuid import uuid4
from app.db.mongodb import db
from app.services.sentiment_service import detect_emotion

MAX_MESSAGES = 10  # keep last N messages total



def create_conversation() -> str:
    conversation_id = str(uuid4())
    db.conversations.insert_one({
        "conversation_id": conversation_id,
        "title": "New chat",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "messages": [],
    })
    return conversation_id


def get_conversation(conversation_id: str) -> list[dict]:
    convo = db.conversations.find_one(
        {"conversation_id": conversation_id},
        {"_id": 0} # include everything except MongoDB _id
    )
    # return convo["messages"] if convo else []
    return convo # could be None if not found


def add_message(conversation_id: str, role: str, content: str, emotion: str | None = None):
    message = {
        "role": role,
        "timestamp": datetime.utcnow(),
        "content": content,
    }

    if emotion:
        message["emotion"] = emotion

    db.conversations.update_one(
        {"conversation_id": conversation_id},
        {
            "$push": {
                "messages": {
                    "$each": [message],
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


def list_conversations(limit: int = 20):
    return list(
        db.conversations.find(
            {},
            {
                "_id": 0,               # don't include MongoDB _id
                "conversation_id": 1,
                "title": 1,
            }
        )
        .sort("updated_at", -1)
        .limit(limit)
    )


def rename_conversation_by_id(conversation_id: str, new_title: str):
    result = db.conversations.update_one(
        {"conversation_id": conversation_id},
        {"$set": {
            "title": new_title,
            "updated_at": datetime.utcnow()
            }
        }
    )
    return result


def delete_conversation_by_id(conversation_id: str):
    result = db.conversations.delete_one({"conversation_id": conversation_id})
    return result
