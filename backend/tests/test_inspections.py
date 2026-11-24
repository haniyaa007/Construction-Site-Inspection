def make_project(client, name="Tower A"):
    return client.post("/projects", json={"name": name}).json()["id"]


def test_create_inspection(client):
    project_id = make_project(client)
    response = client.post("/inspections", json={"project_id": project_id})
    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project_id
    assert body["status"] == "created"


def test_create_inspection_for_unknown_project(client):
    response = client.post("/inspections", json={"project_id": 999})
    assert response.status_code == 404


def test_list_inspections_filtered_by_project(client):
    p1 = make_project(client, "Tower A")
    p2 = make_project(client, "Bridge B")
    client.post("/inspections", json={"project_id": p1})
    client.post("/inspections", json={"project_id": p1})
    client.post("/inspections", json={"project_id": p2})

    response = client.get(f"/inspections?project_id={p1}")
    assert len(response.json()) == 2


def test_get_inspection_not_found(client):
    response = client.get("/inspections/999")
    assert response.status_code == 404