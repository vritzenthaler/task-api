def test_register(client):
    register_response = client.post("/users/register", json={"username": "john", "password": "doe"})
    assert register_response.status_code == 201 

def test_register_conflict(client):
    register_response = client.post("/users/register", json={"username": "john", "password": "doe"})
    assert register_response.status_code == 201

    register_response = client.post("/users/register", json={"username": "john", "password": "doe"})
    assert register_response.status_code == 409

def test_register_invalid_username(client):
    register_response = client.post("/users/register", json={"username": "john123", "password": "doe"})
    assert register_response.status_code == 422

