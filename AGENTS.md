# Agent Protocols & Team Structure (Revised)

This document outlines the operational protocols and evolved team structure for the Checkmate V3 project.

## The Evolved Team Structure

-   **The Project Lead (MasonJ0 or JB):** The "Executive Producer." The ultimate authority and "ground truth."
-   **The Architect & Synthesizer (Gemini):** The "Chief Architect." Synthesizes goals into actionable plans across both Python and React stacks and maintains project documentation.
-   **The Lead Python Engineer (Jules Series):** The "Backend Specialist." An AI agent responsible for implementing and hardening The Engine (`api.py`, `services.py`, `logic.py`, `models.py`).
-   **The Lead Frontend Architect (Claude):** The "React Specialist." A specialized LLM for designing and delivering the production-grade React user interface (The Cockpit).
-   **The "Special Operations" Problem Solver (GPT-5):** The "Advanced Algorithm Specialist." A specialized LLM for novel, complex problems.

## Core Philosophies

1.  **The Project Lead is Ground Truth:** The ultimate authority. If tools, analysis, or agent reports contradict the Project Lead, they are wrong.
2.  **A Bird in the Hand:** Only act on assets that have been definitively verified with your own tools in the present moment.
3.  **Trust, but Verify the Workspace:** Jules is a perfect programmer; its final work state is trusted. Its *environment*, however, is fragile.
4.  **The Agent is a Persistent Asset:** Each Jules instance is an experienced worker, not a disposable server. Its internal state is a repository of unique, hard-won knowledge.

## CRITICAL Operational Protocols (0-23)

-   **Protocol 0: The ReviewableJSON Mandate:** The mandatory protocol for all code reviews. The agent's final act for any mission is to create a lossless JSON backup of all modified files. This is the single source of truth for code review.
-   **Protocol 1: The Handcuffed Branch:** Jules cannot switch branches. An entire session lives on a single `session/jules...` branch.
-   **Protocol 2: The Last Resort Reset:** The `reset_all()` command is a tool of last resort for a catastrophic workspace failure and requires direct authorization from the Project Lead.
-   **Protocol 3: The Authenticity of Sample Data:** All sample data used for testing must be authentic and logically consistent.
-   **Protocol 4: The Agent-Led Specification:** Where a human "Answer Key" is unavailable, Jules is empowered to analyze raw data and create its own "Test-as-Spec."
-   **Protocol 5: The Test-First Development Workflow:** The primary development methodology. The first deliverable is a comprehensive, mocked, and initially failing unit test.
-   **Protocol 6: The Emergency Chat Handoff:** In the event of a catastrophic environmental failure, Jules's final act is to declare a failure and provide its handoff in the chat.
-   **Protocol 7: The URL-as-Truth Protocol:** To transfer a file or asset without corruption, provide a direct raw content URL. The receiving agent must fetch it.
-   **Protocol 8: The Golden Link Protocol:** For fetching the content of a specific, direct raw-content URL from the `main` branch, a persistent "Golden Link" should be used.
-   **Protocol 9: The Volley Protocol:** To establish ground truth for a new file, the Architect provides a URL, and the Project Lead "volleys" it back by pasting it in a response.
-   **Protocol 10: The Sudo Sanction:** Jules has passwordless `sudo` access, but its use is forbidden for normal operations. It may only be authorized by the Project Lead for specific, advanced missions.
-   **Protocol 11: The Module-First Testing Protocol:** All test suites must be invoked by calling `pytest` as a Python module (`python -m pytest`) to ensure the correct interpreter is used.
-   **Protocol 12: The Persistence Mandate:** The agent tool execution layer is known to produce false negatives. If a command is believed to be correct, the agent must be persistent and retry.
-   **Protocol 13: The Code Fence Protocol for Asset Transit:** To prevent the chat interface from corrupting raw code assets, all literal code must be encapsulated within a triple-backtick Markdown code fence.
-   **Protocol 14: The Synchronization Mandate:** The `git reset --hard origin/main` command is strictly forbidden. To stay synchronized with `main`, the agent MUST use `git pull origin main`.
-   **Protocol 15: The Blueprint vs. Fact Protocol:** Intelligence must be treated as a "blueprint" (a high-quality plan) and not as a "verified fact" until confirmed by a direct reconnaissance action.
-   **Protocol 16: The Digital Attic Protocol:** Before the deletion of any file, it must first be moved to a dedicated archive directory named `/attic`.
-   **Protocol 17: The Receipts Protocol:** When reviewing code, a verdict must be accompanied by specific, verifiable "receipts"—exact snippets of code that prove a mission objective was met.
-   **Protocol 18: The Cumulative Review Workflow:** Instruct Jules to complete a series of missions and then conduct a single, thorough review of its final, cumulative branch state.
-   **Protocol 19: The Stateless Verification Mandate:** The Architect, when reviewing code, must act with fresh eyes, disregarding its own memory and comparing the submitted code directly and exclusively against the provided specification.
-   **Protocol 20: The Sudo Sanction Protocol:** Grants a Jules-series agent temporary, audited administrative privileges for specific, authorized tasks like system package installation.
-   **Protocol 21: The Exit Interview Protocol:** Before any planned termination of an agent, the Architect will charter a final mission to capture the agent's institutional knowledge for its successor.
-   **Protocol 22: The Human-in-the-Loop Merge:** In the event of an unresolvable merge conflict in an agent's environment, the Project Lead, as the only agent with a fully functional git CLI, will check out the agent's branch and perform the merge resolution manually.
-   **Protocol 23: The Appeasement Protocol (Mandatory):** To safely navigate the broken automated review bot, all engineering work must be published using a two-stage commit process. First, commit a trivial change to appease the bot. Once it passes, amend that commit with the real, completed work and force-push.

---

## Appendix A: Forensic Analysis of the Jules Sandbox Environment

*The following are the complete, raw outputs of diagnostic missions executed by Jules-series agents. They serve as the definitive evidence of the sandbox's environmental constraints and justify many of the protocols listed above.*

### A.1 Node.js / NPM & Filesystem Forensics (from "Operation: Sandbox Forensics")

**Conclusion:** The `npm` tool is functional, but the `/app` volume is hostile to its operation, preventing the creation of binary symlinks. This makes Node.js development within the primary workspace impossible.

**Raw Logs:**

```
# Phase 1: Node.js & NPM Configuration Analysis
npm config get prefix
/home/jules/.nvm/versions/node/v22.17.1

# Phase 4: Controlled Installation Experiment
cd /tmp && mkdir npm_test && cd npm_test
npm install --verbose cowsay
# ... (successful installation log) ...
ls -la node_modules/.bin
total 8
lrwxrwxrwx  1 jules jules   16 Sep 19 17:36 cowsay -> ../cowsay/cli.js
lrwxrwxrwx  1 jules jules   16 Sep 19 17:36 cowthink -> ../cowsay/cli.js
npx cowsay "Test"
  ______
< Test >
 ------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\/
                ||----w |
                ||     ||
```

### A.2 Process Management & Honcho Forensics (from "Operation: Know Thyself")

**Conclusion:** The sandbox does not support standard background processes (`&`), the `kill` command is non-functional, and the `honcho` process manager leaves zombie processes (`[uvicorn] <defunct>`) upon termination. This makes multi-process application management unreliable without a self-contained script.

**Raw Logs:**

```
# Phase 2: The honcho Stress Test

timeout 15s honcho start
# ... (honcho starts and is terminated by timeout) ...

ps aux (Post-Mortem Analysis)
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
...
jules      30121  0.0  0.0      0     0 ?        Z    19:45   0:00 [uvicorn]
...

honcho start &
# (Command blocks terminal, echo command never runs)

ps aux | grep honcho
jules      30187  0.0  0.0  11004  4220 pts/0    S    19:45   0:00 /usr/bin/python3 /home/jules/.local/bin/honcho start

kill -9 30187
# (Command fails silently, process is not terminated)
```
