from app.tools.registry import get_tool
from app.tools.schema_registry import validate_tool_arguments


def validate_tool_decision(decision: dict):

    if not isinstance(decision, dict):
        raise ValueError("Invalid tool decision.")

    tool_name = decision.get("tool")
    arguments = decision.get("arguments", {})

    if not tool_name:
        raise ValueError(
        f"No tool specified. LLM output: "
        f"{decision.get('raw_output', decision)}"
    )

    tool = get_tool(tool_name)

    if tool is None:
        raise ValueError(
            f"Unauthorized tool: {tool_name}"
        )

    if not isinstance(arguments, dict):
        raise ValueError(
            "Tool arguments must be an object."
        )

    validated_arguments = validate_tool_arguments(
        tool_name,
        arguments
    )

    return {
        "tool": tool_name,
        "arguments": validated_arguments
    }