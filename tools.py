import json
from typing import Annotated

from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL


@tool
def python_repl(code: Annotated[str, "The python code to execute."]):
    """Use this to execute python code. Anything printed is visible to the user.
    Returns a string indicating if the script was executed successfully or not.
    """

    result = ""
    repl = PythonREPL()
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"

    if (result == ""):
        return ""
    else:
        return "StdErr:\n" + result


@tool
def validate_json(json_str: Annotated[str, "The string to check."]):
    """Check if the string is a valid non-empty JSON array.
    Returns True if it is, False otherwise.
    """

    try:
        json_arr = json.loads(json_str)
        if (type(json_arr) == list and len(json_arr) > 0):
            return True
        else:
            return False
    except json.JSONDecodeError:
        return False
