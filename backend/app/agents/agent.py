from app.tools.registry import get_tool
from app.agents.router import classify_question


def run_agent(question: str):

    intent = classify_question(question)

    if intent == "RAG":

        tool = get_tool("rag_search")

        result = tool["function"](
            question=question
        )

        return {
            "question": question,
            "intent": intent,
            "tool": "rag_search",
            "result": result
        }

    if intent == "DATABASE":

        tool = get_tool("employee_search")

        department = None

        departments = [
            "Engineering",
            "Sales",
            "Human Resources"
        ]

        for name in departments:
            if name.lower() in question.lower():
                department = name
                break

        result = tool["function"](
            department=department
        )

        return {
            "question": question,
            "intent": intent,
            "tool": "employee_search",
            "result": result
        }

    if intent == "CALCULATOR":

        return {
            "question": question,
            "intent": intent,
            "tool": "calculator",
            "message": "Calculator requires a mathematical expression."
        }

    return {
        "question": question,
        "intent": "GENERAL",
        "tool": None,
        "result": "I don't know how to handle this question yet."
    }