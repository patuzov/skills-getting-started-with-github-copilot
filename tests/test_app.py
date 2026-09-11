import sys
from copy import deepcopy
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app import activities, app


ORIGINAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))


client = TestClient(app)


def test_get_activities_returns_data():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert len(payload["Chess Club"]["participants"]) == 2


def test_signup_adds_participant():
    email = "newstudent@mergington.edu"

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_rejects_duplicate_email():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_email():
    email = "newstudent@mergington.edu"
    signup_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200

    delete_response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email},
    )

    assert delete_response.status_code == 200
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_rejects_unknown_activity():
    response = client.post(
        "/activities/Not Real/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
