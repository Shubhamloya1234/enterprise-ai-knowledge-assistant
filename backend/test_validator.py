from app.agents.validator import validate_tool_decision

# Valid tool
decision = {
    "tool": "calculator",
    "arguments": {
        "expression": "100 * 25"
    }
}

print("Valid decision:")
print(
    validate_tool_decision(decision)
)


# Invalid tool
bad_decision = {
    "tool": "delete_database",
    "arguments": {}
}

print("\nInvalid decision:")

try:
    print(
        validate_tool_decision(bad_decision)
    )
except Exception as e:
    print("Blocked:", e)