from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.dependencies import get_current_user_record
from app.rag.rag_pipeline import ask_question


router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=4000
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10
    )

    source: str | None = Field(
        default=None,
        max_length=255
    )


@router.post("/ask")
def ask(
    request: QuestionRequest,
    current_user=Depends(get_current_user_record)
):
    return ask_question(
        question=request.question,
        top_k=request.top_k,
        source=request.source
    )