from sqlalchemy.orm import Session

from app.models import Conversation, Message


def get_conversation(
    db: Session,
    conversation_id: int,
    user_id: int
):
    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        .first()
    )


def get_conversation_messages(
    db: Session,
    conversation_id: int,
    user_id: int
):
    conversation = get_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id
    )

    if not conversation:
        return None

    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.id.asc())
        .all()
    )


def save_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
    sources: list[dict] | None = None
):
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources=sources
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message
