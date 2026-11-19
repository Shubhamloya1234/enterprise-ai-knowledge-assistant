from app.tools.registry import list_tools, get_tool


print("AVAILABLE TOOLS")
print(list_tools())


print("\nCALCULATOR")

calculator = get_tool("calculator")

print(
    calculator["function"]("100 * 25")
)


print("\nRAG")

rag = get_tool("rag_search")

result = rag["function"](
    "How many days of annual leave do employees receive?"
)

print(result)


print("\nEMPLOYEE DATABASE")
print(
    "Skipped: employee_search requires an authenticated "
    "user_id and database session. Test it through the "
    "authenticated API or dedicated authorization tests."
)