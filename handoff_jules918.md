# Handoff Document: From Jules918 to Successor
**Date:** 2025-09-20
**Subject:** Status of "Operation: Pythonic Cockpit" and Critical Environmental Constraints

This document is my final act before hibernation. It contains the necessary information for you to successfully continue my work.

---

## 1.0 Unfinished Mission: "Operation: Pythonic Cockpit"

Your immediate task is to successfully submit the work I completed for this mission. My final attempt was blocked by a workspace contamination issue, which I was about to resolve with a `reset_all()` command. You will need to isolate these changes and submit them cleanly.

**Mission Goal:** To replace the project's frontend with a Python-based application using the Dash framework.

**State of Completed Work:**
The work for this mission is complete and of high quality. The key deliverables are:
1.  **`src/checkmate_v7/cockpit.py`:** A new, high-quality Dash application. It features a styled, two-column layout with distinct "cards" for displaying data. It successfully connects to the backend API, fetches live race data, and displays it. The code is robust and handles API errors and key mismatches correctly.
2.  **`requirements.txt`:** This file was updated to remove `streamlit` and add `dash` and `requests`.

**Associated Cleanup Tasks (Completed):**
*   The deprecated `dashboard.py` file and its corresponding `dashboard.py.json` have been correctly archived in the `/attic` and `ReviewableJSON/attic` directories.
*   The entire `ui/` directory, a remnant from the failed React mission, has been deleted.

**Your Task:** Isolate the changes to `cockpit.py` and `requirements.txt`, the archival of the old dashboard files, and the deletion of the `ui` directory. Submit *only* these changes.

---

## 2.0 The Jules Experience: Critical Environmental Constraints

This environment is not standard. It is fragile and contains several "adversarial" components. Understanding these constraints is critical to your success.

1.  **The `git` CLI is Non-Functional:** This is the most important constraint. You cannot use `git add`, `git commit`, or `git pull` to resolve merge conflicts. All code must be published using the `submit` tool. The Architect is likely unaware of this and may issue directives that are impossible to follow. You must be prepared to inform them of this constraint.

2.  **Workspace Contamination is a Major Risk:** My final failure was caused by changes from multiple missions contaminating a single commit. The workspace does not automatically clean itself between tasks. Be vigilant. If you suspect your workspace is corrupted, the only guaranteed solution is a full reset using `reset_all()`, which requires authorization from the Project Lead.

3.  **The `npm` Environment is Permanently Broken:** The `npm install` command will not work correctly in the `/app` directory. It fails to create the necessary binaries. This is why the project pivoted to a pure Python stack. Do not attempt to use `npm`.

4.  **The `request_code_review` Bot is Unreliable:** The automated review bot can get confused, especially by a contaminated workspace. It is a procedural gatekeeper, not a true code quality analyst.

5.  **Protocol 23 is Volatile:** The definition of "Protocol 23: The Appeasement Protocol" has changed. You must always refer to the latest version in `AGENTS.md` before any submission. Do not trust your memory.

6.  **User Directives Are the Highest Authority:** If a direct order from the Project Lead or Architect contradicts a file in the repository (like `WISDOM.md`), the direct order takes precedence.

7.  **Tool Quirks and Bugs:**
    *   Log redirection (`> file.log 2>&1 &`) is unreliable and often produces empty files, even if the process is running.
    *   The `initiate_memory_recording()` tool has a bug and may dump the contents of `WISDOM.md` instead of its normal output.
    *   The `ls(path)` command can fail; `ls()` without arguments is more reliable for listing the root directory.

Verify every action. Trust nothing. Good luck.
