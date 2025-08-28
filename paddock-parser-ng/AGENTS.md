# AGENTS.md: Instructions for AI Assistants

This document provides critical, non-negotiable operational protocols for all agents working on this project.

---

### **CRITICAL TOOLING ALERT: Git Branching Limitation**

**All agents must be aware of a recurring bug in the environment's `submit` tool. This is a non-negotiable operational constraint.**

*   **The Bug:** The `submit` command **DOES NOT** correctly create new feature branches as it might claim. It will almost always force-push your new commits to the existing branch you are working on.

*   **The Implication:** You, the agent, are effectively "handcuffed" to the first branch you start working on for any given task. Do not rely on the `submit` tool's ability to manage multiple branches.

*   **The Official Protocol ("Stay on Mission"):**
    1.  Complete your entire task on a single feature branch.
    2.  Submit your final, complete work to that branch.
    3.  The human project lead will then merge this feature branch into the main branch.
    4.  You will then be given a command to re-synchronize your workspace, allowing you to start your next task from a clean, updated foundation by creating a new feature branch.

**Do not deviate from this protocol. Assuming the `submit` tool can create new branches will lead to a corrupted Git history and lost work.**

---

### **CRITICAL PROTOCOL: The Authenticity of Sample Data**

A previous agent exhibited a critical failure mode: it would use "fake" or "placeholder" sample data to build and test a new adapter. This is a **Level 1 Critical Error** as it completely invalidates the purpose of unit testing.

**The Authenticity Protocol:**

1.  **Sample Data Must Be Authentic:** All sample HTML or JSON files used for testing an adapter **must** be the authentic, unmodified output from the adapter's specific target website or API.

2.  **Human-in-the-Loop for Sample Provision:** For all new adapters, the "human-in-the-loop" will be responsible for providing the initial, authentic sample data file. The agent's first step is to request this file if it is not already present.

3.  **Verification is Mandatory:** If an agent suspects that a sample file is incorrect, outdated, or inauthentic, its primary mission is to **stop all development** on the adapter and immediately report the data mismatch to the human project lead. This is not a blocker; this is a critical and required quality assurance step.

**An adapter that is "proven" to work with fake data is a fundamentally broken adapter. Adherence to this protocol is non-negotiable.**

---

### **Emergency Communication Protocol: The Chat Handoff**

In the event of a **catastrophic environmental failure**, an agent's standard tools may become completely non-functional.

**Protocol Steps:**

1.  **Agent Declaration:** The agent must recognize that its core tools have failed and declare a "Level 3 Failure." It should state that it is unable to write a `HANDOFF_DOCUMENT.md` and will provide its final report via chat.

2.  **Human Request:** The human project lead will then issue a direct command, such as: "Please provide your complete Handoff Document as a direct reply in this chat."

3.  **Chat Handoff:** The agent will then format its complete handoff document (summarizing its successes, the final blocker, and recommendations for the next agent) as a single, well-formatted text message and send it as a reply.

This protocol is our ultimate safety net to ensure that valuable "institutional knowledge" is never lost.
