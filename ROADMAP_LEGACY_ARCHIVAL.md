# Strategic Roadmap: Legacy Code Modernization and Archival
**Authored By:** Gemini 1013, The Steward
**Source Intelligence:** Reviewer Jules, Strategic Assessment (Post-Transformation)
**Status:** Approved Strategic Plan

## 1.0 Objective

To formally align the Fortuna Faucet codebase with its current, professional-grade Windows Desktop Application architecture. This will be achieved by identifying and designating obsolete, superseded, and legacy components for archival. The primary goal is to eliminate developer confusion, reduce technical debt, and focus all future efforts on the modern, established architectural stack.

## 2.0 Critical Implementation Mandate

Direct file system rearrangement (`git move`) via automated directives has proven unreliable and is **strictly forbidden** for the operations outlined in this document. The archival of the files listed below must be conducted as a supervised, manual operation during a dedicated repository maintenance window to ensure the integrity of the project's history and structure.

## 3.0 Designated for Archival: Category 1 (Obsolete Launchers & Deployment Scripts)

These files have been entirely superseded by the new `.bat` script ecosystem and the `fortuna_tray.py` application.

**Files to be moved to `attic/`:**
- `run_server.py`
- `run_backend.bat`
- `launch_checkmate.bat`
- `install.sh`
- `Procfile`

**Rationale:** These scripts represent a previous, manual method of execution and are incompatible with the current orchestrated, multi-process desktop architecture. Their presence in the root directory creates confusion.

## 4.0 Designated for Archival: Category 2 (Superseded Web & Utility Components)

These components are precursors to the modern, integrated desktop suite and their functionality has been replaced by more robust and user-friendly tools.

**Files/Directories to be moved to `attic/`:**
- `checkmate_web/` (entire directory)
- `web_server.py`
- `live_monitor.py`
- `launch_dashboard.py`
- `command_deck.py`

**Rationale:** The functionality of these legacy Flask/FastAPI services and Tkinter UIs is now provided by `python_service/api.py`, `fortuna_monitor.py`, and the `fortuna_tray.py` system tray menu.

## 5.0 Read-Only Archive: Category 3 (The Official Code Museum)

The `attic/` directory is the designated project museum and should be treated as a read-only historical reference.

**No action is required on this directory.** It contains valuable context on the project's evolution through different technology stacks (C#, Rust, VBA) and should not be altered.