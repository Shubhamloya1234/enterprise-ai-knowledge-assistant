import uuid
from pathlib import Path

import chromadb  # ty: ignore[unresolved-import]
import pytest  # ty: ignore[unresolved-import]

from app.rag.loader import load_document
from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import add_documents
from app.rag import retriever, rag_pipeline


@pytest.fixture
def isolated_knowledge_base(monkeypatch):
    # Load the actual uploaded document
    source_path = Path(__file__).parent / "uploads" / "test.txt"
    text = load_document(str(source_path))

    documents = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # Generate real embeddings
    embeddings = generate_embeddings(documents)

    # Create isolated ChromaDB collection
    client = chromadb.EphemeralClient()
    collection = client.create_collection(
    name=f"rag_rejection_test_{uuid.uuid4().hex}"
)

    # Store documents
    add_documents(
        documents=documents,
        embeddings=embeddings,
        metadatas=[
            {
                "source": source_path.name,
                "chunk_index": index
            }
            for index in range(len(documents))
        ],
        target_collection=collection
    )

    # Redirect production retriever to isolated collection
    monkeypatch.setattr(retriever, "collection", collection)


@pytest.mark.parametrize(
    "question",
    [
        "What is the company's maternity leave policy?",
        "What is the employee salary structure?",
        "How many sick leaves are provided?"
    ]
)
def test_unanswerable_questions_return_fallback(
    isolated_knowledge_base,
    question
):
    result = rag_pipeline.ask_question(
        question,
        top_k=3
    )

    assert "I don't have enough information" in result["answer"]

    assert isinstance(result["sources"], list)
