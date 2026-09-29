def test_patch_task_without_credentials(client):
    patch_response = client.patch("/tasks/0", json={})
    assert patch_response.status_code == 401 


def test_patch_task_dummy_token(client):
    token="dummy_token"
    patch_response = client.patch("/tasks/0", json={}, headers={'authorization': f'Bearer {token}'})
    assert patch_response.status_code == 401 


def test_patch_task_invalid_id(client,auth_headers_alice):
    patch_response = client.patch("/tasks/0", json={},headers=auth_headers_alice)
    assert patch_response.status_code == 404 


def test_patch_task_null_title(client,auth_headers_alice):
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice)
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]
    patch_response = client.patch(f"/tasks/{task_id}", json={"title": None}, headers=auth_headers_alice)
    assert patch_response.status_code == 422


def test_patch_task_null_done(client,auth_headers_alice):
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice)
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]
    patch_response = client.patch(f"/tasks/{task_id}", json={"done": None}, headers=auth_headers_alice)
    assert patch_response.status_code == 422


def test_patch_task_done(client,auth_headers_alice):
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice)
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]
    patch_response = client.patch(f"/tasks/{task_id}", json={"done": True}, headers=auth_headers_alice)
    assert patch_response.status_code == 200
    assert patch_response.json() == {
        "title": "Task",
        "id": 1,
        "done": True,
    }


def test_patch_task_title(client,auth_headers_alice):
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice)
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]
    patch_response = client.patch(f"/tasks/{task_id}", json={"title": "Other"}, headers=auth_headers_alice)
    assert patch_response.status_code == 200
    assert patch_response.json() == {
        "title": "Other",
        "id": 1,
        "done": False,
    }

def test_patch_task_invalid_title(client,auth_headers_alice):
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice)
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]
    patch_response = client.patch(f"/tasks/{task_id}", json={"title": "Task One"}, headers=auth_headers_alice)
    assert patch_response.status_code == 422


def test_patch_task_empty_data(client,auth_headers_alice):
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice)
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]
    patch_response = client.patch(f"/tasks/{task_id}", json={}, headers=auth_headers_alice)
    assert patch_response.status_code == 200
    assert patch_response.json() == {
        "title": "Task",
        "id": 1,
        "done": False,
    }

def test_patch_task_updates_both_fields(client,auth_headers_alice):
    task_id = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice).json()["id"]

    patch_response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Other", "done": True},
        headers=auth_headers_alice
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["title"] == "Other"
    assert patch_response.json()["done"] is True

    get_response = client.get(f"/tasks/{task_id}", headers=auth_headers_alice)
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Other"
    assert get_response.json()["done"] is True


def test_patch_task_wrong_user(client,auth_headers_alice,auth_headers_bob):
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice)
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]
    patch_response = client.patch(f"/tasks/{task_id}", json={"title": "Other"}, headers=auth_headers_bob)
    assert patch_response.status_code == 404

    patch_response = client.patch(f"/tasks/{task_id}", json={}, headers=auth_headers_alice)
    assert patch_response.status_code == 200
    assert patch_response.json() == {
        "title": "Task",
        "id": 1,
        "done": False,
    }