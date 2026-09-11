from urllib.parse import quote


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert activities["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant(client):
    email = "new.student@mergington.edu"

    response = client.post("/activities/Soccer Team/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Soccer Team"
    }
    activities = client.get("/activities").json()
    assert email in activities["Soccer Team"]["participants"]


def test_signup_supports_url_encoded_activity_names(client):
    email = "new.chess.student@mergington.edu"
    activity_name = quote("Chess Club", safe="")

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    email = "michael@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert participants.count(email) == 1


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_requires_email(client):
    response = client.post("/activities/Soccer Team/signup")

    assert response.status_code == 422


def test_unregister_removes_participant(client):
    email = "michael@mergington.edu"

    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert email not in participants
    assert "daniel@mergington.edu" in participants


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_nonparticipant(client):
    email = "not.registered@mergington.edu"

    response = client.delete("/activities/Soccer Team/signup", params={"email": email})

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }


def test_unregister_requires_email(client):
    response = client.delete("/activities/Soccer Team/signup")

    assert response.status_code == 422
