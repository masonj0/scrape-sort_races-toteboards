# ARCHITECTURAL MANDATE V8.1
Project: Checkmate V7: The Ultimate Engine
Status: LOCKED & FINAL
Date: 2025-09-26

## 1.0 Abstract & Guiding Principles

This document is the final, locked architectural specification for the Checkmate V7 project. It reflects our strategic pivot to a CLI-first, two-stack system. It is required reading for all AI teammates and serves as the single source of truth for the system's design.

### 1.1 The Two-Stack Architecture

The system is composed of two distinct, collaborating technology stacks:

1.  **THE ENGINE (Python Backend):** A powerful, headless data processing and analysis application. Its sole purpose is to perform the heavy lifting and expose its capabilities via a JSON API.
    *   `models.py` - THE BLUEPRINT (Data Structures & Contracts)
    *   `logic.py` - THE BRAIN (Pure, Stateless Analysis)
    *   `services.py` - THE GATEWAY (I/O & Orchestration)
    *   `api.py` - THE CONDUCTOR (Stateless HTTP Interface)

2.  **THE COCKPIT (User Interface):** The project's primary user interface. As of V8.1 and ROADMAP V5.0, this is implemented as a powerful, interactive Text User Interface (TUI) within the `run.py` script. It remains a pure client of The Engine.

### 1.2 Guiding Policies

All implementation work must adhere to policies for Configuration via Environment, Comprehensive Structured Logging, and Graceful Error Handling.

---

## 2.0 Implementation Specification

### 2.1 The Python Engine

The specifications for `models.py`, `logic.py`, `services.py`, and `api.py` remain the canonical blueprint for the Python backend. Their primary role is to serve the Cockpit.

### 2.2 DEPRECATIONS

The primary user interface is now the "Ultimate TUI" defined in `ROADMAP V5.0`. The previously planned React application, along with the original Python-based `dashboard.py`, are now **DEPRECATED** and will be archived.

### 2.3 The Headless Monitor

The `headless_monitor.py` remains a critical, first-class tool for developers and headless agents to monitor the status of The Engine's API. It is an essential part of the project's infrastructure and is not deprecated.