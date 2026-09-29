def test_get_tasks_without_credentials(client):
    get_response = client.get("/tasks")

    assert get_response.status_code == 401

def test_get_tasks_dummy_token(client):
    token = "dummy_token"

    get_response = client.get("/tasks", headers={'authorization': f'Bearer {token}'})

    assert get_response.status_code == 401

def test_get_tasks_empty_list(client, auth_headers_alice):
    get_response = client.get("/tasks", headers=auth_headers_alice)

    assert get_response.status_code == 200
    assert get_response.json() == []

def test_get_task_invalid_id(client, auth_headers_alice):
    get_response = client.get("/tasks/0", headers=auth_headers_alice)
    assert get_response.status_code == 404 

def test_get_task_wrong_user(client, auth_headers_alice, auth_headers_bob):
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice)

    assert create_response.status_code == 201
    assert create_response.json() == {
        "title": "Task",
        "id": 1,
        "done": False,
    }

    get_response = client.get("/tasks/1", headers=auth_headers_bob)
    assert get_response.status_code == 404 

def test_get_list_wrong_user(client, auth_headers_alice, auth_headers_bob):
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers_alice)

    assert create_response.status_code == 201
    assert create_response.json() == {
        "title": "Task",
        "id": 1,
        "done": False,
    }

    get_response = client.get("/tasks", headers=auth_headers_bob)
    assert get_response.status_code == 200
    assert get_response.json() == []

    get_response = client.get("/tasks", headers=auth_headers_alice)
    assert get_response.status_code == 200
    assert get_response.json() == [{"title": "Task","id": 1,"done": False}]