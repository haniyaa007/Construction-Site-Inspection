import io

import pytest
from PIL import Image

from backend import config
from backend.services.detection import YoloDetector, is_flagged


def image_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (64, 48), "gray").save(buffer, format="PNG")
    return buffer.getvalue()


def make_inspection(client, images=1):
    project_id = client.post("/projects", json={"name": "Tower A"}).json()["id"]
    inspection_id = client.post("/inspections", json={"project_id": project_id}).json()["id"]
    for i in range(images):
        client.post(
            f"/inspections/{inspection_id}/upload",
            files={"file": (f"site{i}.png", image_bytes(), "image/png")},
        )
    return inspection_id


def test_analyze_stores_detections_and_flags(client):
    inspection_id = make_inspection(client)
    response = client.post(f"/inspections/{inspection_id}/analyze")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "analyzed"
    assert body["images_analyzed"] == 1
    assert body["detections_total"] == 4
    assert body["flagged_total"] == 1
    assert client.get(f"/inspections/{inspection_id}").json()["status"] == "analyzed"


def test_results_are_linked_to_image_and_pending(client):
    inspection_id = make_inspection(client)
    image_id = client.get(f"/inspections/{inspection_id}/images").json()[0]["id"]
    client.post(f"/inspections/{inspection_id}/analyze")

    results = client.get(f"/inspections/{inspection_id}/results").json()
    assert len(results) == 4
    assert all(r["image_id"] == image_id for r in results)
    assert all(r["review_status"] == "pending" for r in results)


def test_results_flagged_only(client):
    inspection_id = make_inspection(client)
    client.post(f"/inspections/{inspection_id}/analyze")
    flagged = client.get(f"/inspections/{inspection_id}/results?flagged_only=true").json()
    assert len(flagged) == 1
    assert flagged[0]["object_class"] == "NO-Safety Vest"
    assert flagged[0]["confidence"] == 0.55


def test_analyze_multiple_images(client):
    inspection_id = make_inspection(client, images=2)
    body = client.post(f"/inspections/{inspection_id}/analyze").json()
    assert body["images_analyzed"] == 2
    assert body["detections_total"] == 8


def test_analyze_without_images_is_conflict(client):
    inspection_id = make_inspection(client, images=0)
    assert client.post(f"/inspections/{inspection_id}/analyze").status_code == 409


def test_analyze_twice_is_conflict(client):
    inspection_id = make_inspection(client)
    client.post(f"/inspections/{inspection_id}/analyze")
    assert client.post(f"/inspections/{inspection_id}/analyze").status_code == 409


def test_analyze_unknown_inspection(client):
    response = client.post("/inspections/999/analyze")
    assert response.status_code == 404
    assert response.json()["detail"] == "Inspection not found"


def test_results_unknown_inspection(client):
    response = client.get("/inspections/999/results")
    assert response.status_code == 404
    assert response.json()["detail"] == "Inspection not found"


@pytest.mark.parametrize(
    "object_class, confidence, expected",
    [
        ("NO-Hardhat", 0.60, True),
        ("NO-Safety Vest", 0.40, True),
        ("NO-Safety Vest", 0.33, False),   # below the flag threshold
        ("Hardhat", 0.95, False),          # PPE present is never flagged
        ("NO-Mask", 0.90, False),          # masks are not flagged
    ],
)
def test_flag_rules(object_class, confidence, expected):
    assert is_flagged(object_class, confidence) is expected


@pytest.mark.skipif(not config.MODEL_PATH.exists(), reason="model weights not downloaded")
def test_real_model_runs_on_an_image(tmp_path):
    path = tmp_path / "gray.png"
    path.write_bytes(image_bytes())
    detections = YoloDetector(config.MODEL_PATH, config.DETECTION_MIN_CONFIDENCE).detect(path)
    assert isinstance(detections, list)