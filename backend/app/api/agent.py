from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Conversation

from app.agents.executor import execute_agent
from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.services.memory_service import (
    get_conversation_messages,
    save_message
)


router = APIRouter(
    prefix="/agent",
    tags=["AI Agent"]
)


class AgentRequest(BaseModel):
    question: str
    conversation_id: int


@router.post("/ask")
def ask_agent(
    request: AgentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Get conversation history
    messages = get_conversation_messages(
        db=db,
        conversation_id=request.conversation_id,
        user_id=current_user["user_id"]
    )

    if messages is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user["user_id"]
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    conversation_history = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in messages
    ]

    try:
        # Set the conversation title if this is its first question
        if not conversation.title:
            conversation.title = request.question[:100]  # ty: ignore[invalid-assignment]

        # Save the user's message within the transaction
        save_message(
            db=db,
            conversation_id=request.conversation_id,
            role="user",
            content=request.question
        )

        # Execute the agent
        result = execute_agent(
    question=request.question,
    conversation_history=conversation_history,
    user_id=current_user["user_id"],
    db=db
)

        answer = result["answer"]

        # Extract RAG sources from the agent result
        tool_result = result.get("tool_result") or {}
        sources = tool_result.get("sources") or []

        # Save assistant response along with its sources
        save_message(
    db=db,
    conversation_id=request.conversation_id,
    role="assistant",
    content=answer,
    sources=sources
)

        conversation.updated_at = datetime.utcnow()  # ty: ignore[invalid-assignment]

        # Commit everything together
        db.commit()

    except Exception:
        # Roll back all database changes if anything fails
        db.rollback()
        raise

    return {
        "conversation_id": request.conversation_id,
        "question": request.question,
        "answer": answer,
        "intent": result["intent"],
        "tool": result["tool"],
        "tool_result": result["tool_result"]
    }