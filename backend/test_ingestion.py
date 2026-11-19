
import pytest  # ty: ignore[unresolved-import]

from app.rag import ingestion


def test_ingest_txt_document_successfully(tmp_path, monkeypatch):
    # Arrange
    file_path = tmp_path / "employee_policy.txt"
    file_path.write_text(
        "Employees receive 20 days of annual leave.",
        encoding="utf-8"
    )

    stored_data = {}

    def fake_chunk_text(text):
        assert "20 days" in text
        return ["Employees receive 20 days of annual leave."]

    def fake_generate_embeddings(chunks):
        assert len(chunks) == 1
        return [[0.1] * 384]

    def fake_replace_document_chunks(
        source,
        documents,
        embeddings,
        metadatas,
    ):
        stored_data["source"] = source
        stored_data["documents"] = documents
        stored_data["embeddings"] = embeddings
        stored_data["metadatas"] = metadatas

    monkeypatch.setattr(ingestion, "chunk_text", fake_chunk_text)
    monkeypatch.setattr(
        ingestion,
        "generate_embeddings",
        fake_generate_embeddings,
    )
    monkeypatch.setattr(
        ingestion,
        "replace_document_chunks",
        fake_replace_document_chunks,
    )

    # Act
    result = ingestion.ingest_document(str(file_path))

    # Assert
    assert result["filename"] == "employee_policy.txt"
    assert result["chunks"] == 1

    assert stored_data["source"] == "employee_policy.txt"

    assert stored_data["documents"] == [
        "Employees receive 20 days of annual leave."
    ]

    assert stored_data["metadatas"] == [
        {
            "source": "employee_policy.txt",
            "chunk_index": 0,
        }
    ]

    assert len(stored_data["embeddings"]) == 1


def test_ingestion_rejects_empty_document(tmp_path, monkeypatch):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("   \n   ", encoding="utf-8")

    def unexpected_call(*args, **kwargs):
        pytest.fail(
            "Processing should not continue for an empty document"
        )

    monkeypatch.setattr(
        ingestion,
        "chunk_text",
        unexpected_call,
    )

    with pytest.raises(ValueError, match="no readable text"):
        ingestion.ingest_document(str(file_path))


def test_ingestion_rejects_missing_file(tmp_path):
    file_path = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        ingestion.ingest_document(str(file_path))


def test_ingestion_rejects_unsupported_file(tmp_path):
    file_path = tmp_path / "document.docx"
    file_path.write_text("Test document", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file type"):
        ingestion.ingest_document(str(file_path))
