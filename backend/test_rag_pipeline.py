
from app.rag import rag_pipeline


def test_ask_question_returns_retrieved_answer(monkeypatch):
    documents = [
        {
            "content": "Employees receive 20 days of annual leave.",
            "distance": 0.25,
            "source": "leave_policy.txt",
            "chunk_index": 0
        }
    ]

    def fake_retrieve(
        question,
        top_k=3,
        distance_threshold=None,
        source=None
    ):
        return documents

    monkeypatch.setattr(
        rag_pipeline,
        "retrieve_documents",
        fake_retrieve
    )

    def fake_generate_answer(question, context):
        assert question == "How many annual leave days?"
        assert "20 days" in context
        return context

    monkeypatch.setattr(
        rag_pipeline,
        "generate_answer",
        fake_generate_answer
    )

    result = rag_pipeline.ask_question(
        "How many annual leave days?"
    )

    assert "20 days" in result["answer"]
    assert len(result["sources"]) == 1
    assert result["sources"][0]["source"] == "leave_policy.txt"
    assert result["sources"][0]["chunk_index"] == 0


def test_ask_question_handles_no_retrieved_documents(monkeypatch):
    monkeypatch.setattr(
        rag_pipeline,
        "retrieve_documents",
        lambda *args, **kwargs: []
    )

    result = rag_pipeline.ask_question("Unknown company policy?")

    assert result["answer"] == (
        "I don't have enough information in the knowledge base."
    )
    assert result["sources"] == []


def test_ask_question_passes_top_k_and_source(monkeypatch):
    captured = {}

    def fake_retrieve(
        question,
        top_k=3,
        distance_threshold=None,
        source=None
    ):
        captured["question"] = question
        captured["top_k"] = top_k
        captured["source"] = source
        captured["distance_threshold"] = distance_threshold
        return []

    monkeypatch.setattr(
        rag_pipeline,
        "retrieve_documents",
        fake_retrieve
    )

    rag_pipeline.ask_question(
        "What is the leave policy?",
        top_k=5,
        source="leave_policy.txt"
    )

    assert captured["top_k"] == 5
    assert captured["source"] == "leave_policy.txt"
    assert captured["distance_threshold"] == 0.75


def test_ask_question_returns_all_retrieved_sources(monkeypatch):
    documents = [
        {
            "content": "Annual leave is 20 days.",
            "distance": 0.2,
            "source": "leave.txt",
            "chunk_index": 0
        },
        {
            "content": "Employees can work remotely twice a week.",
            "distance": 0.4,
            "source": "remote_work.txt",
            "chunk_index": 2
        }
    ]

    monkeypatch.setattr(
        rag_pipeline,
        "retrieve_documents",
        lambda *args, **kwargs: documents
    )

    monkeypatch.setattr(
        rag_pipeline,
        "generate_answer",
        lambda question, context: context
    )

    result = rag_pipeline.ask_question(
        "Tell me about company policies."
    )

    assert len(result["sources"]) == 2
    assert result["sources"][0]["source"] == "leave.txt"
    assert result["sources"][1]["source"] == "remote_work.txt"
