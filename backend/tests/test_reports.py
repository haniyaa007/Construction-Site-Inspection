from backend.tests.helpers import make_analyzed_inspection, make_inspection


def flagged_detection_id(client, inspection_id):
    return client.get(f"/inspections/{inspection_id}/results?flagged_only=true").json()[0]["id"]


def test_report_unknown_inspection(client):
    response = client.get("/reports/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Inspection not found"


def test_report_requires_analysis(client):
    inspection_id = make_inspection(client)
    response = client.get(f"/reports/{inspection_id}")
    assert response.status_code == 409
    assert response.json()["detail"] == "Inspection has not been analyzed yet"


def test_report_counts_and_metadata(client):
    inspection_id = make_analyzed_inspection(client)
    report = client.get(f"/reports/{inspection_id}").json()
    assert report["project_name"] == "Tower A"
    assert report["images_analyzed"] == 1
    assert report["detections_total"] == 4
    assert report["observations_total"] == 1
    counts = {c["object_class"]: c["count"] for c in report["detection_counts"]}
    assert counts["NO-Safety Vest"] == 2
    assert counts["Person"] == 1


def test_report_lists_flagged_observation_with_source_image(client):
    inspection_id = make_analyzed_inspection(client)
    report = client.get(f"/reports/{inspection_id}").json()
    observation = report["observations"][0]
    assert observation["object_class"] == "NO-Safety Vest"
    assert observation["original_filename"] == "site0.png"
    assert observation["review_status"] == "pending"
    assert report["observations_by_review_status"] == {"pending": 1, "confirmed": 0, "dismissed": 0}


def test_report_reflects_human_review(client):
    inspection_id = make_analyzed_inspection(client)
    detection_id = flagged_detection_id(client, inspection_id)
    client.patch(f"/detections/{detection_id}/review", json={"review_status": "confirmed"})
    report = client.get(f"/reports/{inspection_id}").json()
    assert report["observations_by_review_status"] == {"pending": 0, "confirmed": 1, "dismissed": 0}


def test_report_includes_issues(client):
    inspection_id = make_analyzed_inspection(client)
    client.post("/issues", json={
        "inspection_id": inspection_id, "title": "Worker without vest",
        "severity": "high", "assigned_to": "Site manager",
    })
    report = client.get(f"/reports/{inspection_id}").json()
    assert report["issues_total"] == 1
    assert report["issues_by_status"] == {"open": 1, "in_progress": 0, "resolved": 0}
    assert report["issues"][0]["title"] == "Worker without vest"


def test_markdown_report_is_honest(client):
    inspection_id = make_analyzed_inspection(client)
    response = client.get(f"/reports/{inspection_id}/markdown")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    text = response.text
    assert "Tower A" in text
    assert "requiring human review" in text
    assert "## Limitations" in text
    assert "non-compliant" not in text.lower()  # the report never issues a verdict


def test_markdown_report_requires_analysis(client):
    inspection_id = make_inspection(client)
    assert client.get(f"/reports/{inspection_id}/markdown").status_code == 409