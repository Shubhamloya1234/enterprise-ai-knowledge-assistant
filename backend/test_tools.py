from app.tools.registry import (
    register_tool,
    get_tool,
    list_tools
)


@register_tool(
    "test_tool",
    "A simple test tool"
)
def sample_tool(value: str):
    return {"value": value}


print("Available tools:")
print(list_tools())

tool = get_tool("test_tool")

print("\nTool result:")
print(tool["function"]("Hello Agent"))