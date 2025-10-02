import pytest
import requests
import os

API_HOST = os.getenv("API_HOST", "http://localhost:5000")

def test_api_races_endpoint():
    """
    SPEC: The /api/races endpoint should return a successful response
    and a list of processed race data.
    """
    # ARRANGE
    url = f"{API_HOST}/api/races"

    # ACT
    response = requests.get(url)

    # ASSERT
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    try:
        response_json = response.json()
    except requests.exceptions.JSONDecodeError:
        pytest.fail("Response is not valid JSON.")

    assert isinstance(response_json, list), f"Expected response to be a list, but got {type(response_json)}"