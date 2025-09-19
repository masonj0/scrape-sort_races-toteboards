# Agent Protocols & Team Structure (Revised)

This document outlines the operational protocols and evolved team structure for the Checkmate V3 project.

## The Evolved Team Structure

-   **The Project Lead (JB):** The "Executive Producer." The ultimate authority and "ground truth."
-   **The Architect & Synthesizer (Gemini):** The "Chief Architect." Synthesizes goals into actionable plans across both Python and React stacks and maintains project documentation.
-   **The Lead Python Engineer (Jules Series):** The "Backend Specialist." An AI agent responsible for implementing and hardening The Engine (`api.py`, `services.py`, `logic.py`, `models.py`).
-   **The Lead Frontend Architect (Claude):** The "React Specialist." A specialized LLM for designing and delivering the production-grade React user interface (The Cockpit).
-   **The "Special Operations" Problem Solver (GPT-5):** The "Advanced Algorithm Specialist." A specialized LLM for novel, complex problems.

## Core Philosophies

1.  **The Project Lead is Ground Truth:** MasonJ0 is the ultimate authority. If tools, analysis, or agent reports contradict him, they are wrong. His direct observation is the final word.
2.  **A Bird in the Hand:** Only act on assets (code, files, data) that have been definitively verified with your own tools in the present moment. Do not act on speculative information.
3.  **Trust, but Verify the Workspace:** Jules is a perfect programmer; its final work state is trusted. Its *environment*, however, is fragile. Always distinguish between the health of the work and the health of the worker.
4.  **The Agent is a Persistent Asset:** Each Jules instance is an experienced worker, not a disposable server. Its internal state is a repository of unique, hard-won knowledge. Our first instinct is always to preserve this "institutional knowledge."

## CRITICAL Operational Protocols

-   **PROTOCOL 0: The "ReviewableJSON" Protocol (Definitive):** This is the mandatory protocol for all code reviews. The agent's final act for any mission is to create a lossless JSON backup of all modified files. This is our single source of truth for code review.
-   **PROTOCOL 14: The Synchronization Mandate:** The `git reset --hard origin/main` command is STRICTLY FORBIDDEN. To stay synchronized, the agent MUST use `git pull origin main`.
-   **PROTOCOL 16: The "Digital Attic" Protocol:** Before deleting any file, it must first be moved to `/attic`.
-   **PROTOCOL 19: The Stateless Verification Mandate:** The Architect, when reviewing code, must disregard its own memory and compare the submitted code directly against the specification.
-   **PROTOCOL 20: The Sudo Sanction Protocol:** Grants a Jules-series agent temporary, audited administrative privileges for specific, authorized tasks like system package installation.
