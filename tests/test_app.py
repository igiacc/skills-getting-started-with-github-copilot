import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", allow_redirects=False)
    assert response.status_code in (301, 302, 307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_participant():
    payload = {"email": "new.student@mergington.edu"}
    response = client.post("/activities/Chess Club/signup", params=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new.student@mergington.edu for Chess Club"}
    assert "new.student@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_activity_returns_400_if_already_signed_up():
    payload = {"email": "michael@mergington.edu"}
    response = client.post("/activities/Chess Club/signup", params=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_unknown_activity_returns_404():
    payload = {"email": "student@mergington.edu"}
    response = client.post("/activities/Unknown Activity/signup", params=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_existing_participant():
    payload = {"email": "michael@mergington.edu"}
    response = client.delete("/activities/Chess Club/participants", params=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Removed michael@mergington.edu from Chess Club"}
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404():
    payload = {"email": "missing.student@mergington.edu"}
    response = client.delete("/activities/Chess Club/participants", params=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_unregister_unknown_activity_returns_404():
    payload = {"email": "student@mergington.edu"}
    response = client.delete("/activities/Unknown Activity/participants", params=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
