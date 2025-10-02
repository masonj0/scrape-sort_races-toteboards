import pytest
import requests
import os

API_HOST = os.getenv("API_HOST", "http://localhost:5000")

def test_api_dashboard_endpoint_structure():
    """
    SPEC: The /api/dashboard endpoint should return a successful response
    with a valid JSON structure, including a robust check of the
    'fetcher_failures' (Black Box) data.
    """
    # ARRANGE
    # First, hit the main races endpoint to populate the cache and failure log
    requests.get(f"{API_HOST}/api/races")

    url = f"{API_HOST}/api/dashboard"

    # ACT
    response = requests.get(url)

    # ASSERT
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    try:
        response_json = response.json()
    except requests.exceptions.JSONDecodeError:
        pytest.fail("Response is not valid JSON.")

    assert isinstance(response_json, dict), f"Expected response to be a dict, but got {type(response_json)}"

    # The dashboard should always have a 'status' key
    assert "status" in response_json, "Response JSON is missing required key: 'status'"

    # Regardless of status (stale or ok), it should report failures
    assert "fetcher_failures" in response_json, "Response JSON is missing required key: 'fetcher_failures'"
    assert isinstance(response_json["fetcher_failures"], list), "'fetcher_failures' should be a list."

    # If there are failures, inspect the first one to ensure it has the correct structure
    if response_json["fetcher_failures"]:
        first_failure = response_json["fetcher_failures"][0]
        assert "adapter" in first_failure, "Failure report is missing 'adapter' key"
        assert "error" in first_failure, "Failure report is missing 'error' key"
        assert "message" in first_failure, "Failure report is missing 'message' key"

    if response_json["status"] == "ok":
        expected_keys = [
            "last_updated",
            "total_qualified_races",
        ]
        for key in expected_keys:
            assert key in response_json, f"OK response is missing expected key: '{key}'"
    elif response_json["status"] == "stale":
        assert "message" in response_json, "Stale response should have a 'message' key."
    else:
        pytest.fail(f"Unexpected status value: {response_json['status']}")