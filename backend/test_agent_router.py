from app.agents.router import classify_question


questions = [
    "How many days of annual leave do employees receive?",
    "How many employees are in Engineering?",
    "What is the total salary?",
    "Hello, how are you?"
]


for question in questions:

    intent = classify_question(question)

    print(
        f"Question: {question}"
    )

    print(
        f"Intent: {intent}\n"
    )