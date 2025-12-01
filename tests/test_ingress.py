import requests
import pytest
import time

# Configuration - Ingress is exposed on port 8080, see docker-compose.yml
BASE_URL = "http://localhost:8080"


# Helper to ensure service is up before testing
@pytest.fixture(scope="session", autouse=True)
def wait_for_service():
    """
    Runs once at the start of the entire test session. Waits up to 5 seconds
    for the Nginx/Traefik service to become responsive.
    """
    max_retries = 5
    for _ in range(max_retries):
        try:
            requests.get(BASE_URL)
            return
        except requests.ConnectionError:
            time.sleep(1)
    pytest.fail("Service did not start in time.")


class TestIngressBehavior:

    def test_health_check_authorized(self):
        """
        Scenario: Valid token provided.
        Expectation: 200 OK and content from the backend.
        """
        headers = {"x-pretest": "valid-token"}
        response = requests.get(f"{BASE_URL}/health", headers=headers)

        assert response.status_code == 200
        assert "Auth service is running" in response.text

    def test_auth_rejection_invalid_token(self):
        """
        Scenario: Invalid token provided.
        Expectation: 401 Unauthorized.
        """
        headers = {"x-pretest": "wrong-token"}
        response = requests.get(f"{BASE_URL}/health", headers=headers)

        assert response.status_code == 401

    def test_auth_rejection_missing_header(self):
        """
        Scenario: No token provided.
        Expectation: 401 Unauthorized.
        """
        response = requests.get(f"{BASE_URL}/health")

        assert response.status_code == 401

    def test_custom_error_page_content(self):
        """
        Scenario: 401 error body check.
        Expectation: Nginx returns a specific error string defined in default.conf.
        """
        headers = {"x-pretest": "wrong-token"}
        response = requests.get(f"{BASE_URL}/health", headers=headers)

        # Nginx config has: return 401 "Authentication failed..."
        expected_msg = (
            "Authentication failed: Invalid or missing x-pretest header"
        )
        assert expected_msg in response.text

    def test_404_handling(self):
        """
        Scenario: Authorized request to non-existent path.
        Expectation: Auth passes, Backend returns 404.
        """
        headers = {"x-pretest": "valid-token"}
        response = requests.get(f"{BASE_URL}/force-404", headers=headers)

        assert response.status_code == 404
