# AI-Driven QA Automation Tool

An autonomous "Virtual User" agent effectively capable of quality assurance testing on web applications. It uses a vision-driven approach (acting on what it sees) rather than relying on brittle code selectors, making it immune to minor UI changes.

## 🧠 System Architecture

The system mimics a human tester with three core components: **Brain**, **Eyes**, and **Hands**.

### 1. The Brain (Hierarchical)
To handle complex tests, we use a two-tiered agent system:

*   **Planner Agent** (`core/planner.py`): The "Team Lead".
    *   **Role**: Breaks down high-level tickets (e.g., "Verify Checkout") into a sequential checklist.
    *   **Input**: User Goal + Project Knowledge.
    *   **Output**: A list of granular steps (e.g., `["Login", "Add Item", "Checkout"]`).
*   **Worker Agent** (`core/agent.py`): The "Tester".
    *   **Role**: Executes one step at a time.
    *   **Input**: A single step from the plan.
    *   **Logic**: Uses a LangGraph state machine to Observe -> Think -> Act.

### 2. The Eyes (Visual Grounding)
*   **Module**: `browser/`
*   **Mechanism**: **Set of Marks (SoM)**.
*   **How it works**:
    1.  Injects `grounding.js` into the browser.
    2.  Identifies interactive elements (buttons, inputs) and filters out invisible ones.
    3.  Overlays a unique numeric ID (Red Box) on each element.
    4.  Passes the "Tagged Screenshot" to the Vision Model (GPT-4o/Claude).
    *   *Benefit*: The AI says "Click ID 5" instead of hallucinating complex XPaths.

### 3. The Hands (Execution)
*   **Module**: `core/tools.py` & `browser/manager.py`
*   **Tools**:
    *   `navigate(url)`: Visits a page.
    *   `click_element(id)`: Smart click on the tagged element.
    *   `type_text(id, text)`: Fills forms.
    *   `scroll(direction)`: Moves the viewport.

### 4. Project Spaces (Knowledge Base)
To scale across multiple apps, we use "Project Spaces" in `projects/`.
*   **Config** (`config.yaml`): Stores Base URL and Credentials (injected securely).
*   **Knowledge** (`knowledge.md`): Persistent memory (e.g., "The login button is blue", "Use these credentials").

## 📂 Project Structure

```text
├── core/                   # The Brain
│   ├── agent.py            # Worker Agent (LangGraph Loop)
│   ├── planner.py          # Planner Agent (High-Level Breakdown)
│   ├── knowledge.py        # Project Context Manager
│   ├── tools.py            # LangChain Tool Definitions
│   └── state.py            # Agent State Definition
│
├── browser/                # The Eyes & Hands
│   ├── manager.py          # Playwright Controller
│   └── grounding.js        # Set of Marks Injection Script
│
├── projects/               # Project Spaces
│   └── saucedemo/          # Example Project
│       ├── config.yaml     # Credentials & URL
│       └── knowledge.md    # Context
│
├── scripts/                # Verification Scripts
│   ├── test_hierarchy.py   # Full Planner -> Worker Flow
│   └── test_grounding.py   # Test Vision System
│
└── main.py                 # Entry point for single-task execution
```

## 🚀 Getting Started

### Prerequisites
1.  Install `uv` (Package Manager).
2.  Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`.

### Running the Agent

**1. Hierarchical Mode (Recommended)**
Runs the full Planner + Worker flow on the "SauceDemo" project.
```powershell
uv run scripts/test_hierarchy.py
```

**2. Single Task Mode**
Runs the Worker Agent on a single goal.
```powershell
uv run main.py
```

## 🛠 Features
*   **Self-Correction**: If an action fails, the agent sees the error and retries.
*   **Vision-First**: Works on any website without custom selectors.
*   **Stateful Memory**: Remembers context across the session.
*   **Modular Models**: Swap between GPT-4o and Claude 3.5 Sonnet easily.
