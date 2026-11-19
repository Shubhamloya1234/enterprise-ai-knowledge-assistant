import pytest  # ty: ignore[unresolved-import]

from app.agents import executor


def setup_agent(monkeypatch, intent, tool_name=None, tool_function=None):
    monkeypatch.setattr(
        executor,
        "classify_question",
        lambda question, history: intent
    )

    def fake_get_tool(name):
        if tool_name is None:
            return None

        if name == tool_name:
            return {"function": tool_function}

        return None

    monkeypatch.setattr(
        executor,
        "get_tool",
        fake_get_tool
    )


def test_rag_question_calls_rag_tool(monkeypatch):
    calls = []

    def fake_rag(question):
        calls.append(question)
        return {"answer": "Employees receive 20 days of annual leave."}

    setup_agent(monkeypatch, "RAG", "rag_search", fake_rag)

    monkeypatch.setattr(
        executor,
        "generate_final_answer",
        lambda **kwargs: kwargs["tool_result"]["answer"]
    )

    result = executor.execute_agent(
        "How many annual leave days are provided?"
    )

    assert result["intent"] == "RAG"
    assert result["tool"] == "rag_search"
    assert len(calls) == 1
    assert "20 days" in result["answer"]


def test_database_question_calls_employee_tool(monkeypatch):
    calls = []

    def fake_employee(db, user_id, department=None):
        calls.append((user_id, department))
        return {"count": 2, "employees": []}

    setup_agent(
        monkeypatch,
        "DATABASE",
        "employee_search",
        fake_employee
    )

    monkeypatch.setattr(
        executor,
        "generate_final_answer",
        lambda **kwargs: "Found employees."
    )

    result = executor.execute_agent(
        "Show me employees in Engineering",
        user_id=1,
        db=object()
    )

    assert result["intent"] == "DATABASE"
    assert result["tool"] == "employee_search"
    assert calls == [(1, "Engineering")]


def test_calculator_question_calls_calculator(monkeypatch):
    calls = []

    def fake_calculator(expression):
        calls.append(expression)
        return {"expression": expression, "result": 2500}

    setup_agent(
        monkeypatch,
        "CALCULATOR",
        "calculator",
        fake_calculator
    )

    monkeypatch.setattr(
        executor,
        "generate_final_answer",
        lambda **kwargs: "2500"
    )

    result = executor.execute_agent("Calculate 100 * 25")

    assert result["intent"] == "CALCULATOR"
    assert result["tool"] == "calculator"
    assert calls == ["100 * 25"]
    assert result["answer"] == "2500"


def test_general_question_does_not_call_tool(monkeypatch):
    setup_agent(monkeypatch, "GENERAL")

    result = executor.execute_agent("Hello, how are you?")

    assert result["intent"] == "GENERAL"
    assert result["tool"] is None
    assert result["tool_result"] is None


def test_missing_rag_tool_raises_error(monkeypatch):
    setup_agent(monkeypatch, "RAG")

    with pytest.raises(ValueError, match="Tool not found"):
        executor.execute_agent("Tell me about company policies")


def test_missing_calculator_tool_raises_error(monkeypatch):
    setup_agent(monkeypatch, "CALCULATOR")

    with pytest.raises(ValueError, match="Tool not found"):
        executor.execute_agent("Calculate 100 * 25")


def test_conversation_history_is_passed_to_rag(monkeypatch):
    calls = []

    def fake_rag(question):
        calls.append(question)
        return {"answer": "20 days"}

    setup_agent(monkeypatch, "RAG", "rag_search", fake_rag)

    monkeypatch.setattr(
        executor,
        "generate_final_answer",
        lambda **kwargs: "20 days"
    )

    history = [
        {"role": "user", "content": "Tell me about company leave."},
        {"role": "assistant", "content": "I can help with leave policies."}
    ]

    executor.execute_agent(
        "How many days?",
        conversation_history=history
    )

    assert len(calls) == 1
    assert "How many days?" in calls[0]
    assert "company leave" in calls[0]


def test_extract_expression_handles_symbolic_arithmetic():
    assert executor.extract_expression("Calculate 100 * 25") == "100 * 25"
    assert executor.extract_expression("What is 10 + 20?") == "10 + 20"
    assert executor.extract_expression("Calculate 125 / 5") == "125 / 5"


def test_extract_expression_rejects_question_without_numbers():
    with pytest.raises(ValueError):
        executor.extract_expression("Calculate the total")

def test_extract_expression_handles_natural_language_arithmetic():
    assert executor.extract_expression("What is 10 plus 20?") == "10 + 20"
    assert executor.extract_expression("What is 50 minus 15?") == "50 - 15"
    assert executor.extract_expression("What is 12 multiplied by 5?") == "12 * 5"
    assert executor.extract_expression("What is 100 divided by 4?") == "100 / 4"