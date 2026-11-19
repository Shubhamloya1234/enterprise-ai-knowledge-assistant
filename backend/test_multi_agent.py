
from app.agents import multi_executor


def test_annual_leave_question(monkeypatch):
    question = "How many days of annual leave do employees receive?"

    monkeypatch.setattr(
        multi_executor,
        "choose_tool",
        lambda question: {
            "tool": "rag_search",
            "arguments": {}
        },
    )

    monkeypatch.setattr(
        multi_executor,
        "get_tool",
        lambda name: {
            "function": lambda **kwargs: {"answer": "20 days"}
        },
    )

    monkeypatch.setattr(
        multi_executor,
        "generate_final_answer",
        lambda **kwargs: "Employees receive 20 days of annual leave.",
    )

    result = multi_executor.execute_multi_step_agent(question)

    assert result["steps"]
    assert result["steps"][0]["tool"] == "rag_search"
    assert "20 days" in result["answer"].lower()


def test_invalid_llm_decision_uses_rag_fallback(monkeypatch):
    monkeypatch.setattr(
        multi_executor,
        "choose_tool",
        lambda question: {"tool": None, "arguments": {}},
    )

    monkeypatch.setattr(
        multi_executor,
        "get_tool",
        lambda name: {
            "function": lambda **kwargs: {"answer": "20 days"}
        },
    )

    monkeypatch.setattr(
        multi_executor,
        "generate_final_answer",
        lambda **kwargs: "Employees receive 20 days of annual leave.",
    )

    result = multi_executor.execute_multi_step_agent(
        "How many days of annual leave do employees receive?"
    )

    assert result["steps"][0]["tool"] == "rag_search"
    assert "20 days" in result["answer"]
