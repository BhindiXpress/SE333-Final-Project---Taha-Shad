# SE 333 Final Project – MCP Testing Agent for Apache Commons Lang

**Author:** Taha Shad  
**Course:** SE 333 – Software Testing  
**Instructor:** Prof. Dong Jae Kim 
**Quarter:** Fall 2025  

This repository contains my final project for SE 333.  
The goal of the project is to build an intelligent testing agent that talks to tools through the Model Context Protocol (MCP) and helps explore and test a real Java project, **Apache Commons Lang 3**.

At a high level, the agent can:

- Run Maven tests in the Lang 3 codebase  
- Generate JaCoCo coverage reports  
- Summarize coverage results  
- Propose new JUnit test cases and boundary tests  
- Interact with Git for status and pushing commits  

A separate reflection report explains what I learned from building and using this system:  
**`Reflection_Paper__Taha_Shad.pdf`** (included in this repo).

---

## 1. Repository layout

From the root of this repository:

- `codebase/`  
  Apache Commons Lang 3 project (Java + Maven).  
  - `pom.xml` – Maven configuration (with JaCoCo plugin)  
  - `src/` – production Java source  
  - `target/` – build and test artifacts  
  - `site/jacoco/` – JaCoCo HTML and XML reports after running coverage  

- `main.py`  
  Small entry point for the project (not required for the MCP server, but kept here for completeness).

- `server.py`  
  Main MCP server implemented in Python using **FastMCP**.  
  Defines the agent and registers testing tools.

- `test_tools.py`  
  Collection of Python functions that the MCP server exposes as tools:
  - run Maven tests  
  - generate and summarize JaCoCo coverage  
  - suggest JUnit and boundary tests  
  - basic Git helpers  

- `mcp.json`  
  MCP configuration file that tells the client how to start `server.py`.

- `Reflection_Paper__Taha_Shad.pdf`  
  Two page reflection paper formatted with the IEEE conference template.

- `.gitignore`  
  Ignores Python virtual environment, build outputs, and other temporary files.

- `pyproject.toml`, `uv.lock`  
  Python project metadata and dependency lockfile (used with `uv` or `pip`).

---

## 2. Prerequisites

To run everything end to end you need:

- **Python 3.11+**  
- **Java 21** (Amazon Corretto in my setup)  
- **Maven**  
  - The project uses the Maven wrapper under `codebase/.mvn/`, so you can run the bundled Maven with  
    `.\mvnw.cmd` (Windows).

- **FastMCP** Python library and other Python dependencies  
  - Installed from `pyproject.toml` using either `uv` or plain `pip`.

- An MCP compatible chat client or environment (for example, the MCP integration in VS Code / ChatGPT).

---

## 3. Setup instructions

From the repository root:

### 3.1 Create and activate a virtual environment

```bash
# from repo root
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
