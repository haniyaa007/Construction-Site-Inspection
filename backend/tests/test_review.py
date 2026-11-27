from backend.tests.helpers import first_detection_id, make_analyzed_inspection


def test_confirming_removes_detection_from_pending_queue(client):
    inspection_id = make_analyzed_inspection(client)
    detection_id = first_detection_id(client, inspection_id)

    response = client.patch(f"/detections/{detection_id}/review", json={"review_status": "confirmed"})
    assert response.status_code == 200
    assert response.json()["review_status"] == "confirmed"

    pending = client.get(f"/inspections/{inspection_id}/results?review_status=pending").json()
    assert len(pending) == 3  # the fake detector produces 4


def test_review_rejects_invalid_status(client):
    inspection_id = make_analyzed_inspection(client)
    detection_id = first_detection_id(client, inspection_id)
    response = client.patch(f"/detections/{detection_id}/review", json={"review_status": "banana"})
    assert response.status_code == 422


def test_review_unknown_detection(client):
    response = client.patch("/detections/999/review", json={"review_status": "confirmed"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Detection not found"