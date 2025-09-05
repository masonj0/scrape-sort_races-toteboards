#!/bin/bash
set -e

echo "--- Creating virtual environment ---"
python3 -m venv venv

echo "--- Activating virtual environment ---"
source venv/bin/activate

echo "--- Upgrading pip ---"
pip install --upgrade pip

echo "--- Installing dependencies from requirements.txt ---"
pip install -r requirements.txt

echo "--- Performing editable install of the project ---"
pip install -e .

echo "--- Environment setup complete! ---"
