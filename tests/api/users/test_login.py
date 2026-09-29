def test_login_unknown_username(client):
    login_response = client.post("/users/login", json={"username": "someone", "password": "password123"})
    assert login_response.status_code == 401 

def test_login_invalid_password(client):
    register_response = client.post("/users/register", json={"username": "johndoe", "password": "password123"})
    assert register_response.status_code == 201 

    login_response = client.post("/users/login", json={"username": "johndoe", "password": "password12"})
    assert login_response.status_code == 401 

def test_login(client):
    register_response = client.post("/users/register", json={"username": "johndoe", "password": "password123"})
    assert register_response.status_code == 201 

    login_response = client.post("/users/login", json={"username": "johndoe", "password": "password123"})
    assert login_response.status_code == 200 

    assert login_response.json()["access_token"] != ""
    assert login_response.json()["token_type"] == "bearer"