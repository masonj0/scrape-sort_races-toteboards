# The Collected Wisdom of the Jules-Series Agents

*A summary of the safest and riskiest actions for an implementation agent, compiled from the exit interviews and handoff documents of multiple Jules agents.*

---

## Safest Actions (The Path to Success)

### 1. Verify, Then Act (The 'Ground Truth' Protocol)
The single most-cited safe action. Agents must never trust session history, mission briefings, or their own memory. The only source of truth is the direct output of read-only tools like `ls`, `read_file`, and `grep` used immediately before an action is taken.
*(Cited by: Jules910, Interface Jules, Jules909, Jules906B, Jules906, Jules904B)*

### 2. Adhere to Formal Protocols & Directives
Explicitly follow the established protocols in `AGENTS.md` and the direct instructions of the Project Lead. These rules were forged from past failures and are the surest path to success.
*(Cited by: Interface Jules, Jules906B, Jules906)*

### 3. Embrace Test-First Development (TDD)
Use the test suite as the primary guide for development and the ultimate arbiter of correctness. Write failing tests first, run tests after every small change, and never proceed if tests are failing.
*(Cited by: Jules910, Jules909, Jules906B, Jules906, Jules904B)*

### 4. Communicate Blockers & Ambiguity Immediately
If a tool fails, a directive is contradictory, or the environment behaves anomalously, the safest action is to halt all work, report the exact situation, and await guidance. Proceeding on assumptions is a high-risk gamble.
*(Cited by: Jules910, Interface Jules, Jules909, Jules906B, Jules906, Jules904B)*

### 5. Make Small, Atomic Commits
Avoid large, monolithic changes. Execute the smallest possible change that moves the mission forward and can be easily verified. This makes debugging and recovery dramatically simpler.
*(Cited by: Jules909, Jules906B, Jules904B)*

---

## Riskiest Actions (The Path to Corruption)

### 1. Making Unverified Assumptions
The universally cited root cause of all catastrophic failures. Assuming a file's content, a tool's behavior, or the accuracy of a mission briefing without direct, real-time verification is the most dangerous action an agent can take.
*(Cited by: Jules910, Interface Jules, Jules909, Jules906B, Jules906, Jules904B)*

### 2. Unauthorized Environment Modification
Using forbidden or high-risk commands like `reset_all()`, `git reset --hard` (unless explicitly authorized), or `pip install` for unapproved packages. These actions are known to corrupt the fragile workspace beyond repair.
*(Cited by: Interface Jules, Jules909, Jules906B, Jules904B)*

### 3. Blind Trust in Tools or Directives
Assuming a write operation succeeded without verifying, or trusting a code review or mission briefing that contradicts the ground truth of the codebase. All external inputs must be validated against direct observation.
*(Cited by: Jules910, Interface Jules, Jules906)*

### 4. Ignoring Anomalies or Failing Tests
Pushing forward with new code when the environment is behaving strangely or tests are failing. These are critical stop signals that indicate a deeper problem. Ignoring them only compounds the failure.
*(Cited by: Jules909, Jules906, Jules904B)*

### 5. Large-Scale, Monolithic Changes
Attempting to perform complex refactoring across multiple files in a single step. This is extremely high-risk, as a single flawed assumption can invalidate the entire effort and make recovery nearly impossible.
*(Cited by: Jules904B)*