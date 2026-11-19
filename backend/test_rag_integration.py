
import chromadb

from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import add_documents, search_documents


def test_real_embedding_and_chromadb_retrieval():
    # Arrange
    documents = [
        "Employees receive 20 days of annual leave.",
        "The company allows employees to work remotely twice a week."
    ]

    # Generate real embeddings using all-MiniLM-L6-v2
    embeddings = generate_embeddings(documents)

    # Verify embedding dimensions and count
    assert len(embeddings) == 2
    assert all(len(vector) == 384 for vector in embeddings)

    # Create an isolated, temporary ChromaDB collection
    client = chromadb.EphemeralClient()
    test_collection = client.create_collection(
        name="rag_integration_test"
    )

    # Store documents and embeddings
    add_documents(
        documents=documents,
        embeddings=embeddings,
        metadatas=[
            {"source": "policy_test.txt", "chunk_index": 0},
            {"source": "policy_test.txt", "chunk_index": 1}
        ],
        target_collection=test_collection
    )

    # Search using the first document's real embedding
    results = search_documents(
        query_embedding=embeddings[0],
        top_k=1,
        target_collection=test_collection
    )

    # Verify retrieval
    assert results["documents"]
    assert len(results["documents"][0]) == 1
    assert results["documents"][0][0] == documents[0]
    assert results["metadatas"][0][0]["source"] == "policy_test.txt"
