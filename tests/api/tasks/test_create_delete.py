def test_create_task(client, auth_headers_alice):
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice)

    assert create_response.status_code == 201
    assert create_response.json() == {
        "title": "Task",
        "id": 1,
        "done": False,
    }

def test_create_task_without_credentials(client):
    create_response = client.post("/tasks", json={"title": "Task 1"})
    assert create_response.status_code == 401

def test_create_task_dummy_token(client):
    token = "dummy_token"
    create_response = client.post("/tasks", json={"title": "Task"}, headers={'authorization': f'Bearer {token}'})
    assert create_response.status_code == 401

def test_create_task_rejects_invalid_title(client, auth_headers_alice):
    create_response = client.post("/tasks", json={"title": "Task 1"}, headers=auth_headers_alice)
    assert create_response.status_code == 422


def test_create_task_get_task(client, auth_headers_alice):
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice)
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]
    get_response = client.get(f"/tasks/{task_id}", headers=auth_headers_alice)
    assert get_response.status_code == 200

def test_delete_task_without_credentials(client):
    patch_response = client.delete("/tasks/1")
    assert patch_response.status_code == 401 

def test_delete_invalid_task(client, auth_headers_alice):
    delete_response = client.delete("/tasks/0", headers=auth_headers_alice)
    assert delete_response.status_code == 404

def test_delete_dummy_token(client):
    token = "dummy_token"
    delete_response = client.delete("/tasks/0", headers={'authorization': f'Bearer {token}'})
    assert delete_response.status_code == 401

def test_create_task_delete_task(client, auth_headers_alice):
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice)
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]
    delete_response = client.delete(f"/tasks/{task_id}", headers=auth_headers_alice)
    assert delete_response.status_code == 204


def test_create_task_delete_task_get_task(client, auth_headers_alice):
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice)
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]
    delete_response = client.delete(f"/tasks/{task_id}", headers=auth_headers_alice)
    assert delete_response.status_code == 204

    get_response = client.get(f"/tasks/{task_id}", headers=auth_headers_alice)
    assert get_response.status_code == 404


def test_delete_task_wrong_user(client, auth_headers_alice, auth_headers_bob):
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice)
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]
    delete_response = client.delete(f"/tasks/{task_id}", headers=auth_headers_bob)
    assert delete_response.status_code == 404

    delete_response = client.delete(f"/tasks/{task_id}", headers=auth_headers_alice)
    assert delete_response.status_code == 204