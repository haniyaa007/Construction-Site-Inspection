from backend.tests.helpers import first_detection_id, make_analyzed_inspection, make_inspection


def issue_payload(inspection_id, **overrides):
    payload = {"inspection_id": inspection_id, "title": "Missing guardrail", "severity": "high"}
    payload.update(overrides)
    return payload


def test_create_issue_defaults_to_open(client):
    inspection_id = make_inspection(client)
    response = client.post("/issues", json=issue_payload(inspection_id))
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "open"
    assert body["detection_id"] is None


def test_create_issue_linked_to_detection(client):
    inspection_id = make_analyzed_inspection(client)
    detection_id = first_detection_id(client, inspection_id)
    response = client.post("/issues", json=issue_payload(inspection_id, detection_id=detection_id))
    assert response.status_code == 201
    assert response.json()["detection_id"] == detection_id


def test_create_issue_unknown_inspection(client):
    response = client.post("/issues", json=issue_payload(999))
    assert response.status_code == 404
    assert response.json()["detail"] == "Inspection not found"


def test_create_issue_with_detection_from_another_inspection(client):
    inspection_a = make_analyzed_inspection(client)
    inspection_b = make_analyzed_inspection(client)
    detection_from_a = first_detection_id(client, inspection_a)
    response = client.post("/issues", json=issue_payload(inspection_b, detection_id=detection_from_a))
    assert response.status_code == 404
    assert response.json()["detail"] == "Detection not found in this inspection"


def test_create_issue_rejects_invalid_severity(client):
    inspection_id = make_inspection(client)
    response = client.post("/issues", json=issue_payload(inspection_id, severity="urgent"))
    assert response.status_code == 422


def test_list_issues_with_filters(client):
    inspection_a = make_inspection(client)
    inspection_b = make_inspection(client)
    first = client.post("/issues", json=issue_payload(inspection_a)).json()["id"]
    client.post("/issues", json=issue_payload(inspection_a, title="Second"))
    client.post("/issues", json=issue_payload(inspection_b, title="Other site"))
    client.patch(f"/issues/{first}", json={"status": "resolved"})

    assert len(client.get(f"/issues?inspection_id={inspection_a}").json()) == 2
    assert len(client.get("/issues?status=resolved").json()) == 1
    assert len(client.get("/issues?status=open").json()) == 2


def test_patch_updates_only_sent_fields(client):
    inspection_id = make_inspection(client)
    issue_id = client.post("/issues", json=issue_payload(inspection_id)).json()["id"]

    response = client.patch(f"/issues/{issue_id}", json={"assigned_to": "Site manager", "status": "in_progress"})
    assert response.status_code == 200
    body = response.json()
    assert body["assigned_to"] == "Site manager"
    assert body["status"] == "in_progress"
    assert body["title"] == "Missing guardrail"  # untouched
    assert body["severity"] == "high"            # untouched


def test_patch_rejects_invalid_status(client):
    inspection_id = make_inspection(client)
    issue_id = client.post("/issues", json=issue_payload(inspection_id)).json()["id"]
    assert client.patch(f"/issues/{issue_id}", json={"status": "done-ish"}).status_code == 422


def test_patch_rejects_null_title(client):
    inspection_id = make_inspection(client)
    issue_id = client.post("/issues", json=issue_payload(inspection_id)).json()["id"]
    response = client.patch(f"/issues/{issue_id}", json={"title": None})
    assert response.status_code == 422
    assert response.json()["detail"] == "title cannot be null"


def test_patch_unknown_issue(client):
    response = client.patch("/issues/999", json={"status": "resolved"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Issue not found"