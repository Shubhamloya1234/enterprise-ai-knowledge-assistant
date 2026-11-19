from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Conversation, Message
from app.schemas.memory import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse
)
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/conversations",
    tags=["Memory"]
)


@router.post("/", response_model=ConversationResponse)
def create_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    conversation = Conversation(
        user_id=current_user["user_id"],
        title=request.title
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get("/", response_model=list[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return (
        db.query(Conversation)
        .filter(
            Conversation.user_id == current_user["user_id"]
        )
        .order_by(Conversation.id.desc())
        .all()
    )


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user["user_id"]
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.id.asc())
        .all()
    )

    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "messages": messages
    }


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse
)
def add_message(
    conversation_id: int,
    request: MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user["user_id"]
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    if request.role != "user":
        raise HTTPException(
            status_code=400,
            detail="Clients can only submit user messages."
        )

    message = Message(
        conversation_id=conversation_id,
        role=request.role,
        content=request.content
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user["user_id"]
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    db.delete(conversation)
    db.commit()

    return {
        "message": "Conversation deleted successfully"
    }
