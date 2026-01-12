import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password, get_password_hash

client = TestClient(app)


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def test_register_login_and_protected_endpoint():
    email = unique_email()
    # Register
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Test User",
            "password": "secret123",
            "role": "student",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    user_id = data["id"]

    # Login (form encoded)
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "secret123"},
    )
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # Access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    protected = client.get("/api/v1/resumes/status", headers=headers)
    assert protected.status_code == 200
    body = protected.json()
    assert body["user_id"] == user_id


def test_password_hashing_and_db_flag():
    email = unique_email()
    # Register
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Hash User",
            "password": "pw1234",
            "role": "student",
        },
    )
    assert resp.status_code == 200
    user_id = resp.json()["id"]

    # Verify password hashing functions
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    assert user is not None
    assert verify_password("pw1234", user.hashed_password)
    assert user.is_active is True
    db.close()


def test_admin_role_access():
    admin_email = unique_email()
    # Create admin
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": admin_email,
            "full_name": "Admin User",
            "password": "adminpw",
            "role": "admin",
        },
    )
    assert resp.status_code == 200

    # Login admin
    login = client.post(
        "/api/v1/auth/login",
        data={"username": admin_email, "password": "adminpw"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    admin_check = client.get("/api/v1/auth/check-admin", headers=headers)
    assert admin_check.status_code == 200
    assert admin_check.json()["role"] == "admin"

    # Non-admin should be forbidden
    user_email = unique_email()
    client.post(
        "/api/v1/auth/register",
        json={
            "email": user_email,
            "full_name": "Regular",
            "password": "userpw",
            "role": "student",
        },
    )
    login2 = client.post(
        "/api/v1/auth/login",
        data={"username": user_email, "password": "userpw"},
    )
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    forbidden = client.get("/api/v1/auth/check-admin", headers=headers2)
    assert forbidden.status_code == 403
