def generate_final_answer(question: str, tool_name: str, tool_result):

    if tool_name == "calculator":

        return str(tool_result["result"])

    if tool_name == "employee_search":

        employees = tool_result.get("employees", [])

        if not employees:
            return "No employees found."

        lines = []

        for employee in employees:
            lines.append(
                f'{employee["name"]} — '
                f'{employee["job_title"]} — '
                f'{employee["department"]}'
            )

        return "\n".join(lines)

    if tool_name == "rag_search":

        answer = tool_result.get("answer")

        if answer:
            return answer

        return "I could not find an answer in the company knowledge base."

    return "I could not generate an answer."