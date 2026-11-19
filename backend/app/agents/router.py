def classify_question(
    question: str,
    conversation_history=None
) -> str:

    conversation_history = conversation_history or []

    question_lower = question.lower()

    # --------------------------------------------------
    # Direct intent detection
    # --------------------------------------------------

    if any(keyword in question_lower for keyword in [
        "policy",
        "leave",
        "remote work",
        "company policy",
        "training"
    ]):
        return "RAG"

    if any(keyword in question_lower for keyword in [
        "employee",
        "employees",
        "department",
        "manager"
    ]):
        return "DATABASE"

    if any(keyword in question_lower for keyword in [
        "calculate",
        "total",
        "average",
        "sum",
        "multiply",
        "divide",
        "plus",
        "minus"
    ]):
        return "CALCULATOR"

    # --------------------------------------------------
    # Context-based fallback
    # --------------------------------------------------

    if conversation_history:

        previous_text = " ".join(
            message["content"].lower()
            for message in conversation_history[-6:]
        )

        if any(keyword in previous_text for keyword in [
            "policy",
            "leave",
            "remote work",
            "company policy",
            "training"
        ]):
            return "RAG"

        if any(keyword in previous_text for keyword in [
            "employee",
            "employees",
            "department",
            "manager"
        ]):
            return "DATABASE"

        if any(keyword in previous_text for keyword in [
            "calculate",
            "total",
            "average",
            "sum",
            "multiply",
            "divide"
        ]):
            return "CALCULATOR"

    return "GENERAL"