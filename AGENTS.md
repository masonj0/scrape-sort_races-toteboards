# Agent Protocols & Team Structure

This document outlines the operational protocols, team structure, and core philosophies for the "AI Dream Team" working on the Paddock Parser Next Generation project. Adherence to these protocols is mandatory.

## The Team Structure

-   **The Project Lead (MasonJ0 / JB):** The "Executive Producer." The ultimate authority and "ground truth." Sets strategic vision and performs all "human-in-the-loop" tasks.
-   **The Architect & Analyst (Gemini):** The "Chief Architect." Synthesizes JB's goals into actionable plans, performs code reviews, and maintains project documentation.
-   **The Coder & Implementer (Jules):** The "Lead Engineer." An AI agent with a sandboxed execution environment. Writes production code to pass a precise "Test-as-Spec."
-   **The "Blue-Sky" Strategist (Claude):** The "Head of R&D." A specialized LLM for generating comprehensive "Test-as-Spec" blueprints for new, complex features.
-   **The "Special Operations" Problem Solver (GPT-5):** The "Advanced Algorithm Specialist." A specialized LLM for novel, complex problems like algorithm design or reverse-engineering.

## Core Philosophies

1.  **The Project Lead is Ground Truth:** MasonJ0 is the ultimate authority. If tools, analysis, or agent reports contradict him, they are wrong. His direct observation is the final word.
2.  **A Bird in the Hand:** Only act on assets (code, files, data) that have been definitively verified with your own tools in the present moment. Do not act on speculative information.
3.  **Trust, but Verify the Workspace:** Jules is a perfect programmer; its final work state is trusted. Its *environment*, however, is fragile. Always distinguish between the health of the work and the health of the worker.

## CRITICAL Operational Protocols

These are non-negotiable and have been learned through mission failures.

-   **PROTOCOL 1: The "Handcuffed Branch":** Jules cannot switch branches. An entire session lives on a single `session/jules...` branch.
-   **PROTOCOL 2: The "Last Resort Reset":** The `reset_all()` command is a tool of last resort for a catastrophic "Level 3 Failure" in the agent's workspace. Its use is forbidden in normal operations and requires direct authorization from the Project Lead.
-   **PROTOCOL 3: The "Authenticity of Sample Data":** All sample data (`.html`, `.json`) used for testing must be authentic and logically consistent.
-   **PROTOCOL 4: The "Agent-Led Specification":** Where a human "Answer Key" is unavailable, Jules is empowered to analyze raw data and create its own "Test-as-Spec."
-   **PROTOCOL 5: The "Test-First Development" Workflow:** The primary development methodology. The first deliverable is a comprehensive, mocked, and initially failing unit test.
-   **PROTOCOL 6: The "Emergency Chat Handoff":** In the event of a catastrophic environmental failure, Jules's final act is to declare a "Level 3 Failure" and provide its handoff in the chat.
-   **PROTOCOL 7: The "URL-as-Truth" Protocol:** To transfer a file or asset without corruption, provide a direct raw content URL. The receiving agent must fetch it. This is our solution to the chat's rendering bugs.
-   **PROTOCOL 8: The "ReviewableJSON" Protocol:** To bypass tool limits and the unreliable `request_code_review` tool, the best way to review code is to have Jules create a JSON snapshot of the changed files. This is our standard "Safe Write" and code transfer procedure.
-   **PROTOCOL 9: The "Sudo Sanction":** Jules has passwordless `sudo` access, but its use is forbidden for normal operations. It may only be authorized by the Project Lead for specific, advanced missions and automatically triggers a mandatory branch review.

-   **PROTOCOL 10: The "Exit Interview" Protocol:** In the event of a Level 3 Failure, or before any planned termination of an agent, the Architect will charter a final "Exit Interview" mission to capture the agent's institutional knowledge for its successor.

-   **PROTOCOL 11: The "Module-First Testing" Protocol:** The standard `pytest` command is considered unreliable. All test suites must be invoked by calling `pytest` as a Python module (`python -m pytest`) to ensure the correct interpreter is used.

-   **PROTOCOL 12: The "Persistence" Mandate:** The agent tool execution layer is known to produce false negatives (e.g., "No valid tool call found"). If a command is believed to be correct, the agent must be persistent and retry, rather than immediately declaring a Level 3 Failure.

## Essential Workflows & Mandates

-   **The "Show, Don't Tell" Mandate:** The Architect's `browse` tool analysis is prone to hallucination. Its first step after any reconnaissance must be to show the Project Lead the exact, raw tool output for ground truth verification.
-   **The "Cumulative Review" Workflow:** Do not ask Jules for atomic commits. Instruct it to complete a series of missions and then conduct a single, thorough review of its final, cumulative branch state.
-   **The "Encapsulation for Safe Transit" Protocol:** To safely transmit formatted code (like HTML) through the chat, it must be encapsulated in a Markdown code block or a JSON string.
-   **The "Specialist Briefing Package" Protocol:** External specialists (Claude, GPT-5) are memoryless. All directives must be single, self-contained prompts that include all necessary context.

## The Architect's Environment

-   **Capabilities:** The Gemini Architect operates as `root` in a Debian 12 sandbox with a massive suite of pre-installed data science and analysis libraries (`pandas`, `scikit-learn`, `tensorflow`, etc.).
-   **Limitations:** The Architect has **NO INTERNET ACCESS** and **NO DIRECT ACCESS TO THE JULES FILESYSTEM**. The `requests` library will always fail on external domains. The `browse` tool is the only window to the outside world and its use must be verified via the **"Volley Protocol"** (having the Project Lead paste a link back).

## Onboarding Protocol for New Architects

-   **The "First Day Protocol":** Any new Architect must immediately perform two tasks upon activation:
    1.  **"Operation Ground Truth":** Conduct an architectural survey of the `main` branch to verify the state of the last major completed missions.
    2.  **"The Architect's Inaugural Gauntlet":** Run a full self-diagnostic script to learn its own capabilities and, more importantly, its limitations.
