from app.tools.schemas import (
    RAGToolArguments,
    EmployeeSearchArguments,
    CalculatorArguments
)


TOOL_SCHEMAS = {
    "rag_search": RAGToolArguments,
    "employee_search": EmployeeSearchArguments,
    "calculator": CalculatorArguments
}


def validate_tool_arguments(
    tool_name: str,
    arguments: dict
):
    schema = TOOL_SCHEMAS.get(tool_name)

    if schema is None:
        raise ValueError(
            f"No schema registered for tool: {tool_name}"
        )

    validated = schema.model_validate(arguments)

    return validated.model_dump()
