def test_login_unknown_username(client):
    login_response = client.post("/users/login", json={"username": "someone", "password": "Il0v3y0u*"})
    assert login_response.status_code == 401 

def test_login_invalid_password(client,auth_headers_alice):
    login_response = client.post("/users/login", json={"username": "alice", "password": "password123"})
    assert login_response.status_code == 401 

def test_login_empty_password(client,auth_headers_alice):
    login_response = client.post("/users/login", json={"username": "alice", "password": ""})
    assert login_response.status_code == 422 

def test_login_non_ascii_password(client,auth_headers_alice):
    login_response = client.post("/users/login", json={"username": "alice", "password": "Aa1!" + "😀" * 28})
    assert login_response.status_code == 422 

def test_login_empty_username(client):
    login_response = client.post("/users/login", json={"username": "", "password": "Il0v3y0u*"})
    assert login_response.status_code == 422 

def test_login_too_long_password(client,auth_headers_alice):
    login_response = client.post("/users/login", json={"username": "alice", "password": "Il0v3y0u*Il0v3y0u*Il0v3y0u*Il0v3y0u*Il0v3y0u*"})
    assert login_response.status_code == 422 

def test_login_too_long_username(client):
    login_response = client.post("/users/login", json={"username": "alicealicealicealicealicealicealicealice", "password": "Il0v3y0u*"})
    assert login_response.status_code == 422 