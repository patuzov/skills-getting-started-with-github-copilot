import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


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
