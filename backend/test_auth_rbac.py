
import time

import jwt
import pytest  # ty: ignore[unresolved-import]
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import JWT_SECRET, JWT_ALGORITHM
from app.core.security import decode_access_token


client = TestClient(app)


def make_token(role="ADMIN", user_id=1, **extra_claims):
    now = int(time.time())

    payload = {
        "user_id": user_id,
        "role": role,
        "iat": now,
        "exp": now + 1800,
        **extra_claims,
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def auth_headers(role="ADMIN", user_id=None):

    if user_id is None:
        user_id = {
            "ADMIN": 1,
            "MANAGER": 2,
            "EMPLOYEE": 3
        }.get(role, 1)

    return {
        "Authorization": f"Bearer {make_token(role, user_id)}"
    }

def test_protected_profile_requires_authentication():
    response = client.get("/protected/profile")
    assert response.status_code == 401


def test_protected_profile_accepts_valid_token():
    response = client.get(
        "/protected/profile",
        headers=auth_headers("MANAGER", 42),
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == 42
    assert response.json()["role"] == "MANAGER"


def test_invalid_token_is_rejected():
    response = client.get(
        "/protected/profile",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_admin_endpoint_allows_admin():
    response = client.get("/rbac/admin", headers=auth_headers("ADMIN"))
    assert response.status_code == 200
    assert response.json()["role"] == "ADMIN"


@pytest.mark.parametrize("role", ["MANAGER", "EMPLOYEE"])
def test_admin_endpoint_rejects_non_admin(role):
    response = client.get("/rbac/admin", headers=auth_headers(role))
    assert response.status_code == 403


def test_manager_endpoint_allows_manager():
    response = client.get(
        "/rbac/manager",
        headers=auth_headers("MANAGER"),
    )
    assert response.status_code == 200
    assert response.json()["role"] == "MANAGER"


@pytest.mark.parametrize("role", ["ADMIN", "EMPLOYEE"])
def test_manager_endpoint_rejects_other_roles(role):
    response = client.get(
        "/rbac/manager",
        headers=auth_headers(role),
    )
    assert response.status_code == 403


def test_employee_endpoint_allows_employee():
    response = client.get(
        "/rbac/employee",
        headers=auth_headers("EMPLOYEE"),
    )
    assert response.status_code == 200
    assert response.json()["role"] == "EMPLOYEE"


@pytest.mark.parametrize("role", ["ADMIN", "MANAGER"])
def test_employee_endpoint_rejects_other_roles(role):
    response = client.get(
        "/rbac/employee",
        headers=auth_headers(role),
    )
    assert response.status_code == 403


def test_expired_token_is_rejected():
    expired_token = make_token(
        "ADMIN",
        exp=int(time.time()) - 60,
    )

    response = client.get(
        "/protected/profile",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401


def test_users_endpoint_requires_admin():
    # No token: HTTPBearer rejects the request before querying MySQL.
    response = client.get("/users/")
    assert response.status_code == 401

    # A non-admin token is rejected before the database query.
    response = client.get(
        "/users/",
        headers=auth_headers("MANAGER"),
    )
    assert response.status_code == 403

# ---------------- JWT SECURITY EDGE CASES ----------------


@pytest.mark.parametrize(
    "missing_claim",
    ["user_id", "role", "iat", "exp"],
)
def test_missing_required_claim_is_rejected(missing_claim):
    now = int(time.time())

    payload = {
        "user_id": 1,
        "role": "ADMIN",
        "iat": now,
        "exp": now + 1800,
    }

    payload.pop(missing_claim)

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)


@pytest.mark.parametrize("user_id", [0, -1, "1", True])
def test_invalid_user_id_is_rejected(user_id):
    token = make_token(user_id=user_id)

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)


@pytest.mark.parametrize("role", ["", "   ", None, 123])
def test_invalid_role_is_rejected(role):
    token = make_token(role=role)

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)


def test_token_signed_with_wrong_secret_is_rejected():
    token = jwt.encode(
        {
            "user_id": 1,
            "role": "ADMIN",
            "iat": int(time.time()),
            "exp": int(time.time()) + 1800,
        },
        "wrong-secret-that-is-not-the-real-key",
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)


def test_token_with_wrong_algorithm_is_rejected():
    token = jwt.encode(
        {
            "user_id": 1,
            "role": "ADMIN",
            "iat": int(time.time()),
            "exp": int(time.time()) + 1800,
        },
        JWT_SECRET,
        algorithm="HS384",
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)

def test_deleted_user_cannot_access_admin_endpoint():
    response = client.get(
        "/rbac/admin",
        headers=auth_headers("ADMIN", user_id=2147483647),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User account no longer exists"


def test_stale_jwt_role_cannot_grant_admin_access():
    # User ID 2 is a MANAGER in the database.
    # The JWT deliberately claims ADMIN.
    response = client.get(
        "/rbac/admin",
        headers=auth_headers("ADMIN", user_id=2),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"