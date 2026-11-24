def test_create_project(client):
    response = client.post("/projects", json={"name": "Tower A", "location": "Islamabad"})
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Tower A"
    assert body["location"] == "Islamabad"
    assert body["id"] == 1


def test_create_project_rejects_empty_name(client):
    response = client.post("/projects", json={"name": ""})
    assert response.status_code == 422


def test_list_projects_starts_empty(client):
    response = client.get("/projects")
    assert response.status_code == 200
    assert response.json() == []


def test_list_projects_returns_created_projects(client):
    client.post("/projects", json={"name": "Tower A"})
    client.post("/projects", json={"name": "Bridge B"})
    response = client.get("/projects")
    assert [p["name"] for p in response.json()] == ["Tower A", "Bridge B"]


def test_get_project_not_found(client):
    response = client.get("/projects/999")
    assert response.status_code == 404