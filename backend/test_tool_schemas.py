from app.agents.validator import validate_tool_decision


valid = {
    "tool": "calculator",
    "arguments": {
        "expression": "100 * 25"
    }
}

print("VALID:")
print(validate_tool_decision(valid))


invalid = {
    "tool": "calculator",
    "arguments": {
        "expression": 12345
    }
}

print("\nINVALID:")

try:
    print(validate_tool_decision(invalid))
except Exception as e:
    print("Blocked:", e)