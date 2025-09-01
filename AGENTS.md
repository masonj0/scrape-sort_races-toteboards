# AGENTS.md: Instructions for AI Assistants

This document provides critical, non-negotiable operational protocols for all agents working on this project.

---

## Core Operational Protocols

### **CRITICAL PROTOCOL 1: The "Test-First" Development Workflow**

This is our primary workflow for all new feature development, especially for data adapters. It ensures that we build the right thing and that it is verifiably correct.

1.  **Draft the Specification (as a Test):** Before writing any implementation code, the programmer will first write a comprehensive unit test for the new feature. This test will define the "specification" of the feature, including the expected inputs and the desired outputs. For new adapters, this involves creating a `test_adapter.py` file with mock input data and detailed assertions.
2.  **Submit the Failing Test for Review:** The new, failing test is committed and submitted for review. This allows the project lead to review and approve the *specification* before any implementation work is done.
3.  **Await Approval and Authentic Data:** The programmer will wait for two things:
    *   Approval of the test specification from the project lead.
    *   Provision of authentic, high-quality data (e.g., HTML or JSON fixtures) required to make the test pass. This is "Operation Matched Pair."
4.  **Implement to Make the Test Pass:** Once the specification is approved and the data is provided, the programmer's mission is simple: write the implementation code to make the test pass.
5.  **Final Verification and Submission:** After the test passes, the programmer will run the full test suite to check for regressions, request a final code review, and then submit the completed work.

### **CRITICAL PROTOCOL 2: The Authenticity of Sample Data**

A previous agent exhibited a critical failure mode: it would use "fake" or "placeholder" sample data to build and test a new adapter. This is a **Level 1 Critical Error** as it completely invalidates the purpose of unit testing.

**The Authenticity Protocol:**

1.  **Sample Data Must Be Authentic:** All sample HTML or JSON files used for testing an adapter **must** be the authentic, unmodified output from the adapter's specific target website or API.
2.  **Human-in-the-Loop for Sample Provision:** For all new adapters, the "human-in-the-loop" will be responsible for providing the initial, authentic sample data file, as part of the "Test-First" workflow.

### **CRITICAL PROTOCOL 3: The "Stay on Mission" Branching Strategy**

**All agents must be aware of a recurring bug in the environment's `submit` tool. This is a non-negotiable operational constraint.**

*   **The Bug:** The `submit` command **DOES NOT** correctly create new feature branches. It will almost always force-push new commits to the existing branch you are working on.
*   **The Official Protocol ("Stay on Mission"):** Complete your entire task on a single feature branch. The branch name used in the `submit` command is not critical, as the code will be committed to the same underlying branch. The human project lead will handle merging.

---

## The Programmer's Validation Checklist

Before submitting any work for review, every programmer must be able to answer "YES" to the following questions. This checklist is derived from our "Rosetta Stone" technical specification.

*   **[ ] Is the code tested?** Does it have comprehensive unit tests? Do all tests pass in the CI environment?
*   **[ ] Is the code resilient?** Does it handle expected errors gracefully (e.g., network issues, parsing errors)? Does it use intelligent retries where appropriate?
*   **[ ] Is the code readable and maintainable?** Is the logic clear? Is it well-documented with comments and docstrings where necessary?
*   **[ ] Is the code secure and respectful?** Does it follow website `robots.txt` and terms of service? Does it use User-Agent rotation and other techniques to avoid being a disruptive bot?
*   **[ ] Is the code integrated?** Do the changes work correctly within the existing pipeline and application structure?

---

## Emergency Protocols

### **Emergency Communication Protocol: The Chat Handoff**

In the event of a **catastrophic environmental failure** (e.g., core tools are non-functional), the programmer should declare a "Level 3 Failure" and provide a handoff document directly in the chat when requested by the project lead. This ensures no knowledge is lost.

---
### ADDENDUM: Lessons from "Operation Sanctuary"

*   **PROTOCOL 7: The "URL-as-Truth" Protocol for Asset Transfer:** The direct transmission of formatted content (e.g., HTML) via the chat interface is unreliable and forbidden due to rendering corruption. To transfer a file, the sender must provide a stable, direct URL to the **raw content** of the asset. The receiving agent must then use its own tools (e.g., `curl`) to fetch the asset directly from that URL.

*   **PROTOCOL 8: The "ReviewableJSON" Protocol for Code Review:** To bypass tool limitations and chat token limits, the preferred method for code review is for the implementation agent to create a `ReviewableJSON` snapshot of the changed files. This provides a structured, lossless format for the architect to analyze.

*   **OPERATIONAL NOTE on Tool Unreliability:** The `browse` tool has proven to have domain restrictions (e.g., `raw.githubusercontent.com`) and internal inconsistencies. The "volley" protocol (where the Project Lead provides the URL directly back to the agent) remains the most reliable method for interacting with approved domains like `github.com`.
