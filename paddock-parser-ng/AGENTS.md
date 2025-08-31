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

### **CRITICAL PROTOCOL 4: The 'Provided Code' Workflow**

On occasion, the human-in-the-loop may provide complete source files (e.g., a new adapter and its corresponding test). This workflow is an alternative to the standard "Test-First" protocol and has its own set of responsibilities.

1.  **Acknowledge and Receive:** The agent will first acknowledge the user's intent to provide code and wait to receive all necessary files (e.g., source code, test code, sample data).
2.  **Integrate and Refactor:** The agent's primary technical task is to integrate the provided files into the existing project structure. This includes:
    *   Placing the files in the correct directories.
    *   **Crucially, refactoring the code to match the project's established conventions and quality standards.** This may involve fixing typos, correcting import paths, removing boilerplate, and ensuring the code is readable and maintainable.
3.  **Verify and Validate:** The agent must run the provided tests and the full existing test suite to verify the new code's functionality and ensure it does not introduce any regressions. The agent is responsible for diagnosing and fixing any issues that arise during testing.
4.  **Submit for Review:** Once the code is integrated, refactored, and fully tested, the agent will submit the work for a final code review.

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
