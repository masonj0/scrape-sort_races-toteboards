# A Hybrid Data Analysis System for Racing Analytics

This repository contains the source code for a sophisticated data analysis system for animal racing (e.g., horse, greyhound). The project serves as a case study in modern system architecture, demonstrating a clean separation of concerns between a data-processing backend and a rich user interface.

The system is designed to fetch data from various sources, apply custom analytical models, and track the historical performance of those models in a "closed-loop."

## Core Architectural Principles

Our development is guided by four core principles to create a resilient, intelligent, and ethical analytical ecosystem.

1.  **Resilient & Human-like Data Fetching:** The system is designed for robust data acquisition, with a focus on resilient, multi-source fetching patterns and sophisticated error handling.
2.  **Feedback-Driven Architecture:** This is a "closed-loop" learning system. It is architected to compare its own analysis against official results, enabling a feedback mechanism to measure and refine the performance of its analytical models over time.
3.  **Hybrid Analytical Model:** The system combines traditional quantitative algorithms with other analytical techniques, creating a hybrid model for a more nuanced and robust analysis.
4.  **Ethical Data Acquisition:** All data fetching is designed to operate within ethical boundaries, respecting data source policies and ensuring a reasonable, human-like access footprint.

## System Architecture

This project utilizes a two-stack architecture to leverage the best technology for each part of the system.

### 1. Python Backend Engine

A powerful, headless Python application that serves as the system's data and analysis core.

*   **Technology:** FastAPI, SQLAlchemy, Pydantic
*   **Responsibilities:**
    *   Manages a modular system of data adapters for fetching information from numerous sources.
    *   Performs complex data processing and normalization.
    *   Runs a pluggable analysis engine to apply custom scoring algorithms.
    *   Serves all processed data and analytical results via a versioned JSON API.

### 2. React User Interface

A modern, interactive web application that acts as the client for the Python backend.

*   **Technology:** React, TypeScript
*   **Responsibilities:**
    *   Provides a rich user interface for visualizing data and analytical insights.
    *   Consumes all data exclusively from the backend's JSON API.
    *   Displays performance metrics and historical model performance.

## Getting Started

### Prerequisites

*   Python 3.9+ and Pip
*   Node.js and npm
*   An active Python virtual environment is highly recommended.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/masonj0/scrape-sort_races-toteboards.git
    cd scrape-sort_races-toteboards
    ```
2.  **Install Backend Dependencies:**
    ```bash
    # From the root directory
    cd src/checkmate_v7
    pip install -r requirements.txt
    ```
3.  **Install Frontend Dependencies:**
    ```bash
    # (Instructions to be added once the frontend directory is established)
    # cd ../../ui
    # npm install
    ```

## Usage

The system is run as two separate processes.

1.  **Run the Backend API Server:**
    *   Navigate to the `src/checkmate_v7` directory.
    *   Start the FastAPI server using uvicorn:
    ```bash
    uvicorn api:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

2.  **Run the Frontend Application:**
    *   (Instructions to be added once the frontend is built.)
    *   Typically, this will involve a command like `npm start` from the UI directory.

## Current Status

The backend API is functional and capable of serving analyzed race data. Active development is focused on building out the React user interface to visualize this data.
