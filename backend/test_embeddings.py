
import numpy as np

from app.rag import embeddings


def test_empty_input_returns_empty_list():
    assert embeddings.generate_embeddings([]) == []


def test_single_text_generates_384_dimensional_embedding(monkeypatch):
    def fake_encode(texts, convert_to_numpy):
        assert texts == ["Employees receive annual leave."]
        assert convert_to_numpy is True
        return np.ones((1, 384))

    monkeypatch.setattr(embeddings.model, "encode", fake_encode)

    result = embeddings.generate_embeddings(
        ["Employees receive annual leave."]
    )

    assert len(result) == 1
    assert len(result[0]) == 384
    assert all(isinstance(value, float) for value in result[0])


def test_multiple_texts_generate_matching_embeddings(monkeypatch):
    def fake_encode(texts, convert_to_numpy):
        return np.ones((len(texts), 384))

    monkeypatch.setattr(embeddings.model, "encode", fake_encode)

    texts = [
        "Annual leave policy.",
        "Work from home policy.",
        "Security training policy."
    ]

    result = embeddings.generate_embeddings(texts)

    assert len(result) == len(texts)
    assert all(len(vector) == 384 for vector in result)


def test_embedding_output_is_a_python_list(monkeypatch):
    def fake_encode(texts, convert_to_numpy):
        return np.ones((1, 384))

    monkeypatch.setattr(embeddings.model, "encode", fake_encode)

    result = embeddings.generate_embeddings(["Test document"])

    assert isinstance(result, list)
    assert isinstance(result[0], list)
