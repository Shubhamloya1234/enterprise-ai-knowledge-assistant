import re

from app.agents.router import classify_question
from app.agents.response_generator import generate_final_answer
from app.tools.registry import get_tool



def build_rag_question(question: str, conversation_history=None) -> str:
    """
    Add the previous user question only when the current
    question is an incomplete follow-up.
    """

    history = conversation_history or []

    follow_up_starters = (
        "how many",
        "how much",
        "what about",
        "and ",
        "why",
        "when",
        "where",
        "does it",
        "is it",
        "are they",
        "can they",
    )

    normalized_question = question.strip().lower()

    is_follow_up = (
        len(normalized_question.split()) <= 6
        and normalized_question.startswith(follow_up_starters)
    )

    if not is_follow_up:
        return question

    previous_user_question = next(
        (
            message["content"]
            for message in reversed(history)
            if message.get("role") == "user"
        ),
        None
    )

    if not previous_user_question:
        return question

    return (
        f"Previous topic: {previous_user_question}\n"
        f"Follow-up question: {question}"
    )



def extract_expression(question: str) -> str:
    question = question.lower()

    replacements = {
        "multiplied by": "*",
        "divided by": "/",
        "plus": "+",
        "minus": "-",
        "times": "*",
        "multiply": "*",
        "divide": "/",
    }

    for word, operator in replacements.items():
        question = question.replace(word, operator)

    matches = re.findall(r"[\d\s+\-*/().]+", question)

    candidates = [
        match.strip()
        for match in matches
        if any(character.isdigit() for character in match)
    ]

    if not candidates:
        raise ValueError("Could not find a mathematical expression.")

    return max(candidates, key=len)


def execute_agent(
    question: str,
    conversation_history=None,
    user_id: int | None = None,
    db=None
):
    """
    Execute the AI agent using deterministic routing.

    conversation_history contains previous messages from
    the current user's conversation.
    """

    conversation_history = conversation_history or []

    # --------------------------------------------------
    # Build contextual question
    # --------------------------------------------------

    contextual_question = question

    if conversation_history:
        previous_context = "\n".join(
            f'{message["role"]}: {message["content"]}'
            for message in conversation_history[-6:]
        )

        contextual_question = (
            f"Previous conversation:\n"
            f"{previous_context}\n\n"
            f"Current question:\n"
            f"{question}"
        )

    # --------------------------------------------------
    # Determine intent
    # --------------------------------------------------

    intent = classify_question(
    question,
    conversation_history
)

    
    
    # --------------------------------------------------
    # RAG
    # --------------------------------------------------

    if intent == "RAG":

        tool_name = "rag_search"

        tool = get_tool(tool_name)

        if tool is None:
            raise ValueError(
                f"Tool not found: {tool_name}"
            )

        rag_question = build_rag_question(
            question,
            conversation_history
        )

        tool_result = tool["function"](
            question=rag_question
        )


    # --------------------------------------------------
    # DATABASE
    # --------------------------------------------------

    
    elif intent == "DATABASE":

        tool_name = "employee_search"

        tool = get_tool(tool_name)

        if tool is None:
            raise ValueError(
                f"Tool not found: {tool_name}"
            )

        department = None

        departments = [
            "Engineering",
            "Sales",
            "Human Resources"
        ]

        for department_name in departments:
            if department_name.lower() in contextual_question.lower():
                department = department_name
                break

        if user_id is None or db is None:
            raise ValueError(
                "Authenticated user context is required for employee search."
            )

        tool_result = tool["function"](
            db=db,
            user_id=user_id,
            department=department
        )
    
    # --------------------------------------------------
    # CALCULATOR
    # --------------------------------------------------

    elif intent == "CALCULATOR":

        tool_name = "calculator"

        tool = get_tool(tool_name)

        if tool is None:
            raise ValueError(
                f"Tool not found: {tool_name}"
            )

        expression = extract_expression(question)

        tool_result = tool["function"](
            expression=expression
        )


    # --------------------------------------------------
    # GENERAL
    # --------------------------------------------------

    else:

        return {
            "question": question,
            "intent": "GENERAL",
            "tool": None,
            "answer": "I don't know how to handle this question yet.",
            "tool_result": None
        }

    # --------------------------------------------------
    # Generate final answer
    # --------------------------------------------------

    final_answer = generate_final_answer(
        question=question,
        tool_name=tool_name,
        tool_result=tool_result
    )

    # --------------------------------------------------
    # Return result
    # --------------------------------------------------

    return {
        "question": question,
        "intent": intent,
        "tool": tool_name,
        "answer": final_answer,
        "tool_result": tool_result
    }