from fastmcp import FastMCP
from test_tools import run_maven_tests  # NEW IMPORT

mcp = FastMCP("se333-testing-agent")


@mcp.tool
def calculator(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    mcp.run(transport="sse")
