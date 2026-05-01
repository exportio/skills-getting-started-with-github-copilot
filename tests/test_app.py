"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_contains_participant_count(self, client):
        """Test that activities include participant information"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "participants" in activity
        assert "max_participants" in activity
        assert isinstance(activity["participants"], list)
        assert isinstance(activity["max_participants"], int)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the list"""
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Programming Class"]["participants"])

        client.post(
            "/activities/Programming Class/signup",
            params={"email": "newstudent@mergington.edu"}
        )

        after_response = client.get("/activities")
        after_count = len(after_response.json()["Programming Class"]["participants"])

        assert after_count == initial_count + 1
        assert "newstudent@mergington.edu" in after_response.json()["Programming Class"]["participants"]

    def test_signup_duplicate_registration_fails(self, client):
        """Test that signing up twice for the same activity fails"""
        email = "duplicate@mergington.edu"

        # First signup
        response1 = client.post(
            "/activities/Gym Class/signup",
            params={"email": email}
        )
        assert response1.status_code == 200

        # Second signup with same email
        response2 = client.post(
            "/activities/Gym Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup for non-existent activity fails"""
        response = client.post(
            "/activities/Fake Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        email = "unregister@mergington.edu"

        # First signup
        client.post(
            "/activities/Art Studio/signup",
            params={"email": email}
        )

        # Then unregister
        response = client.delete(
            "/activities/Art Studio/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "unregistered" in response.json()["message"].lower()

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        email = "remove@mergington.edu"

        # Signup first
        client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )

        # Verify participant is in list
        response = client.get("/activities")
        assert email in response.json()["Drama Club"]["participants"]

        # Unregister
        client.delete(
            "/activities/Drama Club/signup",
            params={"email": email}
        )

        # Verify participant is removed
        response = client.get("/activities")
        assert email not in response.json()["Drama Club"]["participants"]

    def test_unregister_nonexistent_participant_fails(self, client):
        """Test that unregistering a non-existent participant fails"""
        response = client.delete(
            "/activities/Tennis Club/signup",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregistering from non-existent activity fails"""
        response = client.delete(
            "/activities/Fake Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
