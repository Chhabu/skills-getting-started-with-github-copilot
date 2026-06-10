from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


def setup_function():
    # ensure tests start from a known state for mutable in-memory data
    # remove any test email leftovers used across runs
    test_email = "test_student@example.com"
    for act in activities.values():
        if test_email in act["participants"]:
            act["participants"].remove(test_email)


def test_get_activities():
    # Arrange
    client = TestClient(app)

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate_protection():
    # Arrange
    client = TestClient(app)
    activity_name = "Soccer Team"
    email = "test_student@example.com"

    # Make sure the participant is not present before test
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    # Act: sign up the student
    resp = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert successful signup
    assert resp.status_code == 200
    assert email in activities[activity_name]["participants"]

    # Act: attempt duplicate signup
    dup = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert duplicate is rejected
    assert dup.status_code == 400
    assert dup.json().get("detail") == "Student already signed up for this activity"

    # Cleanup
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)


def test_remove_participant():
    # Arrange
    client = TestClient(app)
    activity_name = "Swimming Club"
    email = "test_student@example.com"

    # Ensure participant exists
    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)

    # Act: remove participant
    resp = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity_name]["participants"]
