from .conftest import auth_headers


def test_login_success(client, admin_user):
    resp = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "AdminPass123!"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    assert body["user"]["email"] == "admin@test.com"
    assert body["user"]["role"] == "admin"


def test_login_wrong_password(client, admin_user):
    resp = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "wrong"})
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post("/api/auth/login", json={"email": "nope@test.com", "password": "whatever123"})
    assert resp.status_code == 401


def test_leads_list_requires_auth(client):
    resp = client.get("/api/leads")
    assert resp.status_code == 401


def test_me_requires_valid_token(client):
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer garbage-token"})
    assert resp.status_code == 401


def test_me_returns_current_user(client, member_user):
    headers = auth_headers(client, "member@test.com", "MemberPass123!")
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "member@test.com"


def test_create_user_requires_admin(client, member_user):
    headers = auth_headers(client, "member@test.com", "MemberPass123!")
    resp = client.post("/api/users", json={"email": "new@test.com", "password": "NewPass123!"}, headers=headers)
    assert resp.status_code == 403


def test_create_user_as_admin_succeeds(client, admin_user):
    headers = auth_headers(client, "admin@test.com", "AdminPass123!")
    resp = client.post("/api/users", json={"email": "new@test.com", "password": "NewPass123!"}, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["role"] == "member"
