
from pathlib import Path

from app.rag.loader import load_document
from app.rag.chunker import chunk_text
from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import replace_document_chunks


def ingest_document(file_path: str):
    """
    Complete document ingestion pipeline:

    File -> Text extraction -> Chunking
         -> Embeddings -> ChromaDB
    """

    print(f"Loading document: {file_path}")

    text = load_document(file_path)

    if not text.strip():
        raise ValueError("Document contains no readable text.")

    print("Document loaded.")

    chunks = chunk_text(text)

    if not chunks:
        raise ValueError("Document produced no readable chunks.")

    print(f"Created {len(chunks)} chunks.")

    embeddings = generate_embeddings(chunks)

    print("Embeddings generated.")

    filename = Path(file_path).name

    metadatas = [
        {
            "source": filename,
            "chunk_index": index,
        }
        for index in range(len(chunks))
    ]

    replace_document_chunks(
        source=filename,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print("Document stored in ChromaDB.")

    return {
        "filename": filename,
        "chunks": len(chunks),
    }
