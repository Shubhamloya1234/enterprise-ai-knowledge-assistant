
import hashlib
from pathlib import Path
from typing import Any

import chromadb  # type: ignore


# Always use the backend's ChromaDB directory.
BACKEND_DIR = Path(__file__).resolve().parents[2]
CHROMA_DB_DIR = BACKEND_DIR / "chroma_db"

client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))

collection = client.get_or_create_collection(
    name="enterprise_knowledge"
)


def _generate_chunk_id(
    source: str,
    chunk_index: int,
    document: str,
) -> str:
    """Generate a deterministic ID for a document chunk."""

    content = f"{source}:{chunk_index}:{document}"
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()

    return f"doc_{digest}"


def add_documents(
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict] | None = None,
    target_collection: Any | None = None,
):
    """Insert or update document chunks using deterministic IDs."""

    if not documents:
        return []

    if len(documents) != len(embeddings):
        raise ValueError(
            "Documents and embeddings must have equal lengths."
        )

    if metadatas is not None and len(documents) != len(metadatas):
        raise ValueError(
            "Documents and metadata must have equal lengths."
        )

    destination = (
        target_collection
        if target_collection is not None
        else collection
    )

    normalized_metadatas = []
    ids = []

    for index, document in enumerate(documents):
        metadata = dict(metadatas[index]) if metadatas else {}

        source = str(metadata.get("source", "unknown"))
        chunk_index = int(metadata.get("chunk_index", index))

        metadata["source"] = source
        metadata["chunk_index"] = chunk_index

        normalized_metadatas.append(metadata)

        ids.append(
            _generate_chunk_id(source, chunk_index, document)
        )

    destination.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=normalized_metadatas,
    )

    return ids


def replace_document_chunks(
    source: str,
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
    target_collection: Any | None = None,
):
    """
    Replace all chunks belonging to a source document.

    New chunks are stored before obsolete chunks are deleted.
    """

    destination = (
        target_collection
        if target_collection is not None
        else collection
    )

    if len(documents) != len(embeddings):
        raise ValueError(
            "Documents and embeddings must have equal lengths."
        )

    if len(documents) != len(metadatas):
        raise ValueError(
            "Documents and metadata must have equal lengths."
        )

    for metadata in metadatas:
        if str(metadata.get("source")) != source:
            raise ValueError(
                "All metadata sources must match the document source."
            )

    new_ids = add_documents(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        target_collection=destination,
    )

    existing = destination.get(
        where={"source": source}
    )

    existing_ids = existing.get("ids", [])

    obsolete_ids = [
        chunk_id
        for chunk_id in existing_ids
        if chunk_id not in new_ids
    ]

    if obsolete_ids:
        destination.delete(ids=obsolete_ids)

    return new_ids


def search_documents(
    query_embedding: list[float],
    top_k: int = 5,
    target_collection: Any | None = None,
):
    """Search the selected ChromaDB collection."""

    destination = (
        target_collection
        if target_collection is not None
        else collection
    )

    total = destination.count()

    if total == 0:
        return {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

    return destination.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, total),
    )


def delete_document(source: str):
    """Delete all chunks belonging to a source document."""

    results = collection.get(
        where={"source": source}
    )

    ids = results.get("ids", [])

    if not ids:
        return 0

    collection.delete(ids=ids)

    return len(ids)
