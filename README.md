# Checkmate V7: The Live Cockpit

This project is a real-time, web-based horse racing analysis engine. It leverages a powerful, battle-tested Python backend to fetch and analyze live data from multiple sources, exposing the results through a lightweight and elegant Vanilla JavaScript frontend.

---

## Core Concept

The architecture is a modern, two-stack system as defined in the `ARCHITECTURAL_MANDATE_V8.1.md`:

1.  **THE ENGINE (Python/FastAPI):** A powerful, headless data processing application that performs all heavy lifting and exposes its capabilities via a JSON API.
2.  **THE COCKPIT (Vanilla JS):** A lightweight, single-page web application that serves as the project's primary user interface. It is a pure client of The Engine.

## Getting Started

The application is designed to be run as a local web server.

1.  **Install Dependencies:**
    ```bash
    pip install -r checkmate_web/requirements.txt
    ```
2.  **Run the Web Server:**
    ```bash
    cd checkmate_web
    uvicorn main:app --reload
    ```
3.  **Access the Cockpit:**
    Open a web browser and navigate to `http://127.0.0.1:8000`.

## Project Status

The project is currently executing **Phase 1 of ROADMAP V6.0: "The Engine Room."** The immediate goal is to stand up the core FastAPI server and port our perfected portable engine logic into a modular, web-ready format.