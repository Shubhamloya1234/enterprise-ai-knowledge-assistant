
import pytest  # ty: ignore[unresolved-import]
from pydantic import ValidationError

from app.agents.validator import validate_tool_decision
from app.agents.llm_agent_old import extract_json


def test_extract_valid_json():
    output = 'Some text {"tool":"rag_search","arguments":{"question":"Leave policy"}}'
    result = extract_json(output)

    assert result["tool"] == "rag_search"
    assert result["arguments"]["question"] == "Leave policy"


def test_extract_invalid_json():
    result = extract_json('{"tool": "rag_search", invalid}')
    assert result is None


def test_extract_json_with_no_object():
    result = extract_json("No JSON returned by model.")
    assert result is None


def test_validate_rag_tool():
    result = validate_tool_decision({
        "tool": "rag_search",
        "arguments": {"question": "Leave policy"}
    })

    assert result["tool"] == "rag_search"
    assert result["arguments"]["question"] == "Leave policy"
    assert result["arguments"]["top_k"] == 3


def test_validate_employee_tool():
    result = validate_tool_decision({
        "tool": "employee_search",
        "arguments": {"department": "Engineering"}
    })

    assert result["tool"] == "employee_search"
    assert result["arguments"]["department"] == "Engineering"


def test_validate_calculator_tool():
    result = validate_tool_decision({
        "tool": "calculator",
        "arguments": {"expression": "100 * 25"}
    })

    assert result["tool"] == "calculator"
    assert result["arguments"]["expression"] == "100 * 25"


def test_reject_non_dictionary_decision():
    with pytest.raises(ValueError, match="Invalid tool decision"):
        validate_tool_decision("rag_search")  # ty: ignore[invalid-argument-type]


def test_reject_missing_tool():
    with pytest.raises(ValueError, match="No tool specified"):
        validate_tool_decision({"arguments": {}})


def test_reject_unregistered_tool():
    with pytest.raises(ValueError, match="Unauthorized tool"):
        validate_tool_decision({
            "tool": "delete_database",
            "arguments": {}
        })


def test_reject_non_dictionary_arguments():
    with pytest.raises(ValueError, match="arguments must be an object"):
        validate_tool_decision({
            "tool": "rag_search",
            "arguments": "Leave policy"
        })


def test_reject_empty_rag_question():
    with pytest.raises(ValidationError):
        validate_tool_decision({
            "tool": "rag_search",
            "arguments": {"question": ""}
        })


def test_reject_invalid_rag_top_k():
    with pytest.raises(ValidationError):
        validate_tool_decision({
            "tool": "rag_search",
            "arguments": {
                "question": "Leave policy",
                "top_k": 20
            }
        })


def test_reject_empty_calculator_expression():
    with pytest.raises(ValidationError):
        validate_tool_decision({
            "tool": "calculator",
            "arguments": {"expression": ""}
        })
