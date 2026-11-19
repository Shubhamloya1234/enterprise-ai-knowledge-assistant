from pydantic import BaseModel, Field


class RAGToolArguments(BaseModel):
    question: str = Field(
        min_length=1,
        description="Question to search in the company knowledge base."
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10
    )


class EmployeeSearchArguments(BaseModel):
    name: str | None = None
    department: str | None = None


class CalculatorArguments(BaseModel):
    expression: str = Field(
        min_length=1,
        description="Mathematical expression to calculate."
    )