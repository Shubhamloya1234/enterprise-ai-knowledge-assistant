from app.tools.registry import register_tool
from app.rag.rag_pipeline import ask_question


@register_tool(
    "rag_search",
    "Search the company knowledge base and answer questions using relevant documents."
)
def rag_search(
    question: str,
    top_k: int = 3
):
    return ask_question(
        question=question,
        top_k=top_k
    )