def test_register(client):
    register_response = client.post("/users/register", json={"username": "john", "password": "Il0v3y0u*"})
    assert register_response.status_code == 201 

def test_register_conflict(client):
    register_response = client.post("/users/register", json={"username": "john", "password": "Il0v3y0u*"})
    assert register_response.status_code == 201

    register_response = client.post("/users/register", json={"username": "john", "password": "Il0v3y0u*"})
    assert register_response.status_code == 409

def test_register_invalid_username(client):
    register_response = client.post("/users/register", json={"username": "john123", "password": "Il0v3y0u*"})
    assert register_response.status_code == 422

def test_register_invalid_password_min_length(client):
    register_response = client.post("/users/register", json={"username": "john", "password": "Il0v3y*"})
    assert register_response.status_code == 422

def test_register_invalid_password_max_length(client):
    register_response = client.post("/users/register", json={"username": "john", "password": "*Il0v3yuIl0v3yuIl0v3yuIl0v3yuIl0v3yu"})
    assert register_response.status_code == 422

def test_register_invalid_password_lowercase(client):
    register_response = client.post("/users/register", json={"username": "john", "password": "IL0V3Y0U*"})
    assert register_response.status_code == 422

def test_register_invalid_password_uppercase(client):
    register_response = client.post("/users/register", json={"username": "john", "password": "il0v3y0u*"})
    assert register_response.status_code == 422

def test_register_invalid_password_special_character(client):
    register_response = client.post("/users/register", json={"username": "john", "password": "Il0v3y0u"})
    assert register_response.status_code == 422

def test_register_invalid_password_digit(client):
    register_response = client.post("/users/register", json={"username": "john", "password": "Iloveyou*"})
    assert register_response.status_code == 422

def test_register_non_ascii_password(client):
    login_response = client.post("/users/register", json={"username": "alice", "password": "Aa1!" + "😀" * 28})
    assert login_response.status_code == 422 
