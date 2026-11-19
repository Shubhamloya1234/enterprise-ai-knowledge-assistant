from app.agents.executor import execute_agent


questions = [
    "How many days of annual leave do employees receive?",
    "Show me employees in Engineering",
]


for question in questions:

    print("\n" + "=" * 60)
    print("QUESTION:")
    print(question)

    try:
        result = execute_agent(question)

        print("\nAGENT RESULT:")
        print(result)

    except Exception as e:
        print("\nAGENT ERROR:")
        print(e)