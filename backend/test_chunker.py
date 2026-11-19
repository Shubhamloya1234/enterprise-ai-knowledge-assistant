
import pytest

from app.rag.chunker import chunk_text


def test_empty_text_returns_empty_list():
    assert chunk_text("") == []


def test_short_text_returns_one_chunk():
    text = "Employees receive annual leave."
    assert chunk_text(text) == [text]


def test_long_text_is_split_into_chunks():
    text = "A" * 1200

    chunks = chunk_text(text, chunk_size=500, overlap=50)

    assert len(chunks) == 3
    assert all(len(chunk) <= 500 for chunk in chunks)


def test_chunks_have_expected_overlap():
    text = "A" * 1000

    chunks = chunk_text(text, chunk_size=500, overlap=50)

    assert chunks[0][-50:] == chunks[1][:50]


def test_zero_chunk_size_is_rejected():
    with pytest.raises(ValueError, match="chunk_size"):
        chunk_text("Test", chunk_size=0)


def test_negative_overlap_is_rejected():
    with pytest.raises(ValueError, match="overlap"):
        chunk_text("Test", chunk_size=10, overlap=-1)


def test_overlap_equal_to_chunk_size_is_rejected():
    with pytest.raises(ValueError, match="overlap"):
        chunk_text("Test", chunk_size=10, overlap=10)


def test_overlap_greater_than_chunk_size_is_rejected():
    with pytest.raises(ValueError, match="overlap"):
        chunk_text("Test", chunk_size=10, overlap=12)
