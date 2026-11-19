
from pathlib import Path

import chromadb  # ty: ignore[unresolved-import]

from app.rag.loader import load_document
from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import add_documents, search_documents


def test_actual_document_retrieval_quality():
    # 1. Load the actual uploaded document
    source_path = Path(__file__).parent / "uploads" / "test.txt"
    text = load_document(str(source_path))

    # Split into non-empty lines to preserve individual facts
    documents = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    assert documents, "No readable content found in test.txt"

    # 2. Generate real embeddings
    embeddings = generate_embeddings(documents)

    assert len(embeddings) == len(documents)
    assert all(len(vector) == 384 for vector in embeddings)

    # 3. Create an isolated ChromaDB collection
    client = chromadb.EphemeralClient()
    test_collection = client.create_collection(
        name="rag_quality_test"
    )

    # 4. Store document chunks
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
        target_collection=test_collection
    )

    # 5. Evaluate natural-language questions
    evaluations = [
        (
            "How many annual leave days do employees receive?",
            "20 days"
        ),
        (
            "How often can employees work remotely?",
            "twice a week"
        ),
        (
            "What can employees use the assistant for?",
            "find company policies"
        )
    ]

    for question, expected_fact in evaluations:
        query_embedding = generate_embeddings([question])[0]

        results = search_documents(
            query_embedding=query_embedding,
            top_k=1,
            target_collection=test_collection
        )

        retrieved = results["documents"][0]

        assert retrieved, f"No result retrieved for: {question}"

        actual_text = retrieved[0].lower()

        assert expected_fact.lower() in actual_text, (
            f"\nQuestion: {question}"
            f"\nExpected fact: {expected_fact}"
            f"\nRetrieved text: {actual_text}"
        )
