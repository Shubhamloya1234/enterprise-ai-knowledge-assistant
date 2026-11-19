
from app.rag.retriever import retrieve_documents
from app.rag.llm import generate_answer


def ask_question(
    question: str,
    top_k: int = 3,
    source: str | None = None
):
    documents = retrieve_documents(
        question,
        top_k=top_k,
        distance_threshold=0.75,
        source=source
    )

    if not documents:
        return {
            "question": question,
            "answer": "I don't have enough information in the knowledge base.",
            "sources": []
        }

    context = "\n\n".join(
        document["content"]
        for document in documents
    )

    answer = generate_answer(question, context)

    sources = [
        {
            "source": document["source"],
            "chunk_index": document["chunk_index"],
            "distance": document["distance"]
        }
        for document in documents
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }
