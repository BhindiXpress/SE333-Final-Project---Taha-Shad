import os
import subprocess
import xml.etree.ElementTree as ET
import re


from fastmcp import FastMCP

# MCP server instance for tools in this file
mcp = FastMCP("se333-testing-agent")

# Resolve path to the codebase folder (where pom.xml lives)
PROJECT_ROOT = os.path.dirname(__file__)
CODEBASE_DIR = os.path.join(PROJECT_ROOT, "codebase")


@mcp.tool
def run_maven_tests() -> str:
    """
    Run Maven tests in the codebase and return the tail of the output.
    Uses mvn.cmd on Windows and mvn on other systems.
    """
    try:
        mvn_cmd = "mvn.cmd" if os.name == "nt" else "mvn"

        result = subprocess.run(
            [mvn_cmd, "clean", "test", "-B"],
            cwd=CODEBASE_DIR,
            capture_output=True,
            text=True,
            check=False,
        )

        # Return last 2000 characters of stdout or stderr
        return result.stdout[-2000:] or result.stderr[-2000:]
    except Exception as e:
        return f"Error running mvn test: {e}"


@mcp.tool
def summarize_coverage() -> str:
    """
    Read JaCoCo coverage report and summarize overall coverage.

    Looks for:
      codebase/target/site/jacoco/jacoco.xml
    """
    # Base dir where pom.xml lives
    project_root = os.path.dirname(__file__)
    codebase_dir = os.path.join(project_root, "codebase")

    # Main JaCoCo XML path
    candidates = [
        os.path.join(codebase_dir, "target", "site", "jacoco", "jacoco.xml"),
        os.path.join(codebase_dir, "target", "jacoco.xml"),  # fallback just in case
    ]

    report_path = None
    for p in candidates:
        if os.path.exists(p):
            report_path = p
            break

    if report_path is None:
        return (
            "JaCoCo report not found in expected locations.\n"
            "I looked for:\n"
            + "\n".join(f"  - {p}" for p in candidates)
            + "\n\nRun `run_maven_tests` or `mvn clean test jacoco:report` first."
        )

    try:
        tree = ET.parse(report_path)
        root = tree.getroot()

        lines = [f"JaCoCo coverage summary from: {report_path}"]

        for counter in root.findall("counter"):
            ctype = counter.get("type")
            covered = int(counter.get("covered", "0"))
            missed = int(counter.get("missed", "0"))
            total = covered + missed
            pct = 0.0 if total == 0 else round(covered * 100.0 / total, 1)
            lines.append(f"- {ctype}: {pct}% ({covered}/{total} covered)")

        return "\n".join(lines)

    except Exception as e:
        return f"Error reading JaCoCo report: {e}"

@mcp.tool
def suggest_junit_tests_for_class(class_name: str) -> str:
    """
    Suggest JUnit 4 test method skeletons for a given fully-qualified class name.

    Example input:
      "org.apache.commons.lang3.Range"

    This does NOT modify files; it just returns suggested test methods as text.
    """
    project_root = os.path.dirname(__file__)
    codebase_dir = os.path.join(project_root, "codebase")

    # Translate package name to path
    # e.g. org.apache.commons.lang3.Range -> org/apache/commons/lang3/Range.java
    if "." in class_name:
        pkg_path = class_name.replace(".", os.sep) + ".java"
    else:
        pkg_path = class_name + ".java"

    candidate = os.path.join(codebase_dir, "src", "main", "java", pkg_path)

    if not os.path.exists(candidate):
        return (
            f"Could not find source file for {class_name}.\n"
            f"I looked for: {candidate}"
        )

    try:
        with open(candidate, "r", encoding="ISO-8859-1") as f:
            src = f.read()
    except Exception as e:
        return f"Error reading {candidate}: {e}"

    # Very simple regex to find public methods
    method_pattern = re.compile(
        r"public\s+(static\s+)?[<>\w\[\]]+\s+(\w+)\s*\(",
        re.MULTILINE,
    )
    methods = sorted(set(m.group(2) for m in method_pattern.finditer(src)))

    if not methods:
        return f"No public methods found in {class_name}."

    lines = []
    lines.append(f"Suggested JUnit 4 test skeletons for {class_name}:")
    lines.append("")
    lines.append("```java")
    lines.append("import org.junit.Test;")
    lines.append("import static org.junit.Assert.*;")
    lines.append(f"import {class_name};")
    lines.append("")
    lines.append(f"public class {class_name.split('.')[-1]}GeneratedTest " + "{")
    lines.append("")

    for mname in methods:
        lines.append("    @Test")
        lines.append(f"    public void test_{mname}() " + "{")
        lines.append("        // TODO: arrange inputs")
        lines.append(f"        // {class_name} obj = new {class_name.split('.')[-1]}();")
        lines.append(f"        // Object result = obj.{mname}(/* args */);")
        lines.append("        // assertNotNull(result);")
        lines.append("    }")
        lines.append("")

    lines.append("}")
    lines.append("```")

    return "\n".join(lines)

@mcp.tool
def suggest_boundary_tests(description: str) -> str:
    """
    Suggest boundary and edge-case tests for a method or behavior.

    Example input:
      "Range.between(low, high) with integers"
      "StringUtils.substring(str, start, end)"
    """
    ideas = []
    ideas.append(f"Boundary test ideas for: {description}")
    ideas.append("")
    ideas.append("1. Typical in-range values")
    ideas.append("   - Use normal, expected inputs to confirm the main behavior.")
    ideas.append("")
    ideas.append("2. Lower boundary")
    ideas.append("   - Inputs exactly at the minimum allowed (e.g., min, 0, empty string).")
    ideas.append("   - Check that the method still behaves correctly and does not throw.")
    ideas.append("")
    ideas.append("3. Just below lower boundary")
    ideas.append("   - Inputs slightly below the allowed minimum (e.g., min-1, -1).")
    ideas.append("   - Expect an exception or clear error behavior if the API specifies it.")
    ideas.append("")
    ideas.append("4. Upper boundary")
    ideas.append("   - Inputs exactly at the maximum allowed (e.g., max, length-1).")
    ideas.append("   - Ensure no off-by-one errors.")
    ideas.append("")
    ideas.append("5. Just above upper boundary")
    ideas.append("   - Inputs slightly above the maximum allowed (e.g., max+1, length).")
    ideas.append("   - Expect failure or a well-defined response.")
    ideas.append("")
    ideas.append("6. Null / empty / default values")
    ideas.append("   - Null arguments, empty collections, empty strings, zero-length ranges.")
    ideas.append("   - Check whether the method allows them or throws.")
    ideas.append("")
    ideas.append("7. Degenerate / special cases")
    ideas.append("   - low == high, start == end, negative ranges, NaN, infinities.")
    ideas.append("   - For comparisons, equal values and reversed bounds.")
    ideas.append("")
    ideas.append("8. Large inputs")
    ideas.append("   - Very large numbers, long strings, big collections.")
    ideas.append("   - Look for overflow, performance, or memory issues.")
    ideas.append("")
    ideas.append("9. Invalid combinations")
    ideas.append("   - Start > end, low > high, incompatible flags.")
    ideas.append("   - Ensure clear error handling or documented behavior.")
    ideas.append("")
    ideas.append("Use these categories to design concrete JUnit tests for this API.")

    return "\n".join(ideas)

def _project_root() -> str:
    # Helper to get the folder where server.py / test_tools.py live
    return os.path.dirname(__file__)

@mcp.tool
def git_status() -> str:
    """
    Run 'git status' in the project root and return the output.
    """
    root = _project_root()
    try:
        result = subprocess.run(
            ["git", "-C", root, "status"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error running git status: {e}"

@mcp.tool
def git_add_all() -> str:
    """
    Run 'git add -A' in the project root.
    """
    root = _project_root()
    try:
        result = subprocess.run(
            ["git", "-C", root, "add", "-A"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout or result.stderr or "git add -A completed."
    except Exception as e:
        return f"Error running git add -A: {e}"
@mcp.tool
def git_commit(message: str) -> str:
    """
    Run 'git commit -m <message>' in the project root.
    """
    root = _project_root()
    try:
        result = subprocess.run(
            ["git", "-C", root, "commit", "-m", message],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error running git commit: {e}"
@mcp.tool
def git_push(remote: str = "origin", branch: str = "main") -> str:
    """
    Run 'git push <remote> <branch>' in the project root.

    This will fail gracefully if no remote is configured.
    """
    root = _project_root()
    try:
        result = subprocess.run(
            ["git", "-C", root, "push", remote, branch],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error running git push: {e}"
