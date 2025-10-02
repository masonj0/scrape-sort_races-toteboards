import pytest
import requests
import os

API_HOST = os.getenv("API_HOST", "http://localhost:5000")

def test_api_funnel_endpoint():
    """
    SPEC: The /api/funnel endpoint should return a successful response
    with a valid JSON structure containing funnel statistics.
    """
    # ARRANGE
    url = f"{API_HOST}/api/funnel"

    # ACT
    response = requests.get(url)

    # ASSERT
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    try:
        response_json = response.json()
    except requests.exceptions.JSONDecodeError:
        pytest.fail("Response is not valid JSON.")

    assert isinstance(response_json, dict), f"Expected response to be a dict, but got {type(response_json)}"

    if response_json.get("status") == "stale":
        assert "message" in response_json
    else:
        expected_keys = [
            "races_fetched_by_source",
            "total_races_fetched",
            "races_after_deduplication",
            "races_after_scoring",
            "qualified_races",
        ]
        for key in expected_keys:
            assert key in response_json, f"Response JSON is missing expected key: '{key}'"

        assert isinstance(response_json["races_fetched_by_source"], dict), "'races_fetched_by_source' should be a dictionary."