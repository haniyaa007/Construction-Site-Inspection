import io

from PIL import Image

from backend import config


def make_image_bytes(image_format="PNG", size=(64, 48)):
    buffer = io.BytesIO()
    Image.new("RGB", size, "gray").save(buffer, format=image_format)
    return buffer.getvalue()


def make_inspection(client):
    project_id = client.post("/projects", json={"name": "Tower A"}).json()["id"]
    return client.post("/inspections", json={"project_id": project_id}).json()["id"]


def upload(client, inspection_id, data, filename="site.png", content_type="image/png"):
    return client.post(
        f"/inspections/{inspection_id}/upload",
        files={"file": (filename, data, content_type)},
    )


def test_upload_valid_png(client, tmp_path):
    inspection_id = make_inspection(client)
    response = upload(client, inspection_id, make_image_bytes("PNG"))
    assert response.status_code == 201
    body = response.json()
    assert body["content_type"] == "image/png"
    assert (body["width"], body["height"]) == (64, 48)
    assert len(list((tmp_path / "uploads").iterdir())) == 1


def test_upload_valid_jpeg(client):
    inspection_id = make_inspection(client)
    response = upload(client, inspection_id, make_image_bytes("JPEG"), "site.jpg", "image/jpeg")
    assert response.status_code == 201
    assert response.json()["content_type"] == "image/jpeg"


def test_upload_sets_inspection_status(client):
    inspection_id = make_inspection(client)
    upload(client, inspection_id, make_image_bytes())
    assert client.get(f"/inspections/{inspection_id}").json()["status"] == "uploaded"


def test_upload_to_unknown_inspection(client):
    response = upload(client, 999, make_image_bytes())
    assert response.status_code == 404


def test_upload_rejects_fake_image(client, tmp_path):
    inspection_id = make_inspection(client)
    response = upload(client, inspection_id, b"this is not an image", "fake.jpg", "image/jpeg")
    assert response.status_code == 400
    assert not (tmp_path / "uploads").exists()  # nothing was saved


def test_upload_rejects_empty_file(client):
    inspection_id = make_inspection(client)
    assert upload(client, inspection_id, b"").status_code == 400


def test_upload_rejects_unsupported_format(client):
    inspection_id = make_inspection(client)
    response = upload(client, inspection_id, make_image_bytes("GIF"), "a.gif", "image/gif")
    assert response.status_code == 415


def test_upload_rejects_oversized_file(client, monkeypatch):
    monkeypatch.setattr(config, "MAX_UPLOAD_BYTES", 100)
    inspection_id = make_inspection(client)
    response = upload(client, inspection_id, make_image_bytes(size=(200, 200)))
    assert response.status_code == 413


def test_malicious_filename_cannot_escape_upload_dir(client, tmp_path):
    inspection_id = make_inspection(client)
    response = upload(client, inspection_id, make_image_bytes(), "../../evil.png")
    assert response.status_code == 201
    assert response.json()["original_filename"] == "evil.png"
    assert not (tmp_path / "evil.png").exists()
    assert len(list((tmp_path / "uploads").iterdir())) == 1


def test_list_images(client):
    inspection_id = make_inspection(client)
    upload(client, inspection_id, make_image_bytes(), "one.png")
    upload(client, inspection_id, make_image_bytes(), "two.png")
    response = client.get(f"/inspections/{inspection_id}/images")
    assert [i["original_filename"] for i in response.json()] == ["one.png", "two.png"]