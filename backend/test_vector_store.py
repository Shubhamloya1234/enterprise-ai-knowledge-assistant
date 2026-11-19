
import chromadb  # ty: ignore[unresolved-import]

from app.rag.vector_store import add_documents, search_documents


def test_vector_store_add_and_search():
    client = chromadb.EphemeralClient()

    test_collection = client.create_collection(
        name="vector_store_test"
    )

    documents = [
        "Employees receive 20 days of annual leave.",
        "The company work-from-home policy allows remote work twice a week.",
        "Employees must complete security training every year.",
    ]

    # Synthetic 384-dimensional vectors; no production data is modified.
    embeddings = [
        [0.1] * 384,
        [0.4] * 384,
        [0.7] * 384,
    ]

    add_documents(
        documents,
        embeddings,
        target_collection=test_collection,
    )

    results = search_documents(
        [0.1] * 384,
        top_k=2,
        target_collection=test_collection,
    )

    assert results["ids"]
    assert len(results["ids"][0]) == 2
    assert len(results["documents"][0]) == 2
    assert set(results["documents"][0]).issubset(set(documents))


if __name__ == "__main__":
    test_vector_store_add_and_search()
    print("Vector store test passed!")
