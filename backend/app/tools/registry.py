from typing import Callable


TOOLS = {}


def register_tool(name: str, description: str):
    def decorator(func: Callable):
        TOOLS[name] = {
            "function": func,
            "description": description
        }
        return func

    return decorator


def get_tool(name: str):
    return TOOLS.get(name)


def list_tools():
    return {
        name: {
            "description": tool["description"]
        }
        for name, tool in TOOLS.items()
    }