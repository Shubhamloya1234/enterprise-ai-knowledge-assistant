from app.tools.registry import register_tool


@register_tool(
    "calculator",
    "Perform basic arithmetic calculations."
)
def calculator(expression: str):

    allowed_characters = set(
        "0123456789+-*/(). "
    )

    if not expression:
        raise ValueError(
            "Expression cannot be empty."
        )

    if not all(
        character in allowed_characters
        for character in expression
    ):
        raise ValueError(
            "Invalid characters in expression."
        )

    try:
        result = eval(
            expression,
            {"__builtins__": {}},
            {}
        )

        return {
            "expression": expression,
            "result": result
        }

    except Exception:
        raise ValueError(
            "Invalid mathematical expression."
        )