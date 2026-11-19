
from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import collection


def retrieve_documents(
    query: str,
    top_k: int = 3,
    distance_threshold: float | None = None,
    source: str | None = None,
):
    """
    Retrieve relevant document chunks from ChromaDB.

    If distance_threshold is provided, only results within
    that distance are returned.

    If source is provided, only chunks from that document
    are searched.
    """

    if not query or not query.strip():
        return []

    if top_k < 1:
        return []

    if distance_threshold is not None and distance_threshold < 0:
        raise ValueError("Distance threshold cannot be negative.")

    if collection.count() == 0:
        return []

    query_embedding = generate_embeddings([query])[0]

    where_filter = {"source": source} if source else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        where=where_filter,
    )

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    relevant_documents = []

    for document, distance, metadata in zip(
        documents,
        distances,
        metadatas,
    ):
        if distance_threshold is not None and distance > distance_threshold:
            continue

        metadata = metadata or {}

        relevant_documents.append({
            "content": document,
            "distance": distance,
            "source": metadata.get("source", "unknown"),
            "chunk_index": metadata.get("chunk_index"),
        })

    return relevant_documents
