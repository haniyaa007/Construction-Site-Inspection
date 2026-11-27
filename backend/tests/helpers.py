import io

from PIL import Image


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


def make_analyzed_inspection(client):
    inspection_id = make_inspection(client)
    client.post(f"/inspections/{inspection_id}/analyze")
    return inspection_id


def first_detection_id(client, inspection_id):
    return client.get(f"/inspections/{inspection_id}/results").json()[0]["id"]