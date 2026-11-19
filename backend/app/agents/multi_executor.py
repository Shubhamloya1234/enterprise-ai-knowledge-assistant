
import re

from app.agents.llm_agent_old import choose_tool
from app.agents.validator import validate_tool_decision
from app.agents.response_generator import generate_final_answer
from app.tools.registry import get_tool


MAX_STEPS = 3


def _fallback_tool_decision(question: str) -> dict:
    """Select a registered tool when the LLM returns invalid output."""
    text = question.lower()

    if re.search(
        r"\b(how many days|annual leave|leave policy|"
        r"remote work|work from home|company policy|"
        r"security training|company information)\b",
        text,
    ):
        return {
            "tool": "rag_search",
            "arguments": {"question": question},
        }

    if re.search(
        r"\b(calculate|what is|compute)\b.*\d|"
        r"\d\s*[+*/-]\s*\d",
        text,
    ):
        expression = re.sub(
            r"^(calculate|compute)\s+",
            "",
            text,
            flags=re.IGNORECASE,
        ).strip().rstrip("?")

        return {
            "tool": "calculator",
            "arguments": {"expression": expression},
        }

    if re.search(
        r"\b(employee|employees|department|staff member)\b",
        text,
    ):
        return {
            "tool": "employee_search",
            "arguments": {},
        }

    return {
        "tool": "rag_search",
        "arguments": {"question": question},
    }


def execute_multi_step_agent(question: str):
    tool_results = []
    current_question = question

    for step in range(MAX_STEPS):
        decision = choose_tool(current_question)

        try:
            validated = validate_tool_decision(decision)
        except (ValueError, TypeError, KeyError):
            fallback = _fallback_tool_decision(current_question)
            validated = validate_tool_decision(fallback)

        tool_name = validated["tool"]
        arguments = validated["arguments"]

        tool = get_tool(tool_name)
        if tool is None:
            raise ValueError(f"Tool is not registered: {tool_name}")

        result = tool["function"](**arguments)

        tool_results.append({
            "step": step + 1,
            "tool": tool_name,
            "arguments": arguments,
            "result": result,
        })

        # Current implementation executes one tool per question.
        break

    final_answer = generate_final_answer(
        question=question,
        tool_name=tool_results[-1]["tool"],  # ty: ignore[invalid-argument-type]
        tool_result=tool_results[-1]["result"],
    )

    return {
        "question": question,
        "steps": tool_results,
        "answer": final_answer,
    }
