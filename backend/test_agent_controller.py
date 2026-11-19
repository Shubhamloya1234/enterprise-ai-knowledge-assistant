from app.agents.executor import execute_agent


questions = [
    "How many days of annual leave do employees receive?",
    "Show me employees in Engineering",
    "Calculate 100 * 25"
]


for question in questions:

    print("\n" + "=" * 60)
    print("QUESTION:")
    print(question)

    try:
        result = execute_agent(question)

        print("\nRESULT:")
        print(result)

    except Exception as e:
        print("\nERROR:")
        print(e)