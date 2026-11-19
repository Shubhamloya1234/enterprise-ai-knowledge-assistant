
import pytest  # ty: ignore[unresolved-import]
from pydantic import ValidationError

# Import tool modules so their decorators register the tools.
import app.tools  # noqa: F401

from app.tools.registry import get_tool, list_tools
from app.tools.schemas import (
    RAGToolArguments,
    EmployeeSearchArguments,
    CalculatorArguments,
)
from app.tools.schema_registry import validate_tool_arguments
from app.agents.validator import validate_tool_decision


def test_expected_tools_are_registered():
    tools = list_tools()

    assert "rag_search" in tools
    assert "employee_search" in tools
    assert "calculator" in tools

    for name in ("rag_search", "employee_search", "calculator"):
        assert callable(get_tool(name)["function"])
        assert tools[name]["description"]


def test_rag_arguments_accept_valid_input():
    result = validate_tool_arguments(
        "rag_search",
        {"question": "What is the annual leave policy?"},
    )

    assert result["question"] == "What is the annual leave policy?"
    assert result["top_k"] == 3


def test_rag_arguments_reject_empty_question():
    with pytest.raises(ValidationError):
        RAGToolArguments(question="")


def test_rag_arguments_enforce_top_k_limits():
    with pytest.raises(ValidationError):
        RAGToolArguments(question="Policy?", top_k=0)

    with pytest.raises(ValidationError):
        RAGToolArguments(question="Policy?", top_k=11)


def test_employee_search_accepts_optional_filters():
    result = validate_tool_arguments(
        "employee_search",
        {"name": "Amit", "department": "Sales"},
    )

    assert result["name"] == "Amit"
    assert result["department"] == "Sales"


def test_calculator_rejects_empty_expression():
    with pytest.raises(ValidationError):
        CalculatorArguments(expression="")


def test_unknown_tool_schema_is_rejected():
    with pytest.raises(ValueError, match="No schema registered"):
        validate_tool_arguments("unknown_tool", {})


def test_validator_accepts_registered_tool():
    result = validate_tool_decision(
        {
            "tool": "rag_search",
            "arguments": {"question": "What is the leave policy?"},
        }
    )

    assert result["tool"] == "rag_search"
    assert result["arguments"]["top_k"] == 3


def test_validator_rejects_unauthorized_tool():
    with pytest.raises(ValueError, match="Unauthorized tool"):
        validate_tool_decision(
            {"tool": "unknown_tool", "arguments": {}}
        )


def test_validator_rejects_non_object_arguments():
    with pytest.raises(ValueError, match="arguments must be an object"):
        validate_tool_decision(
            {"tool": "rag_search", "arguments": ["not", "an", "object"]}
        )


def test_validator_rejects_missing_tool():
    with pytest.raises(ValueError, match="No tool specified"):
        validate_tool_decision(
            {"arguments": {"question": "What is the leave policy?"}}
        )
