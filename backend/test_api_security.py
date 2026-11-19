from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_current_user_record
from app.core.security import create_access_token
from app.db.database import get_db
from app.api import documents, rag


def make_headers(user_id=1, role="ADMIN"):
    token = create_access_token(user_id=user_id, role=role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def set_user():
    def override(role, user_id=1):
        app.dependency_overrides[get_current_user_record] = lambda: SimpleNamespace(
            id=user_id,
            role=role,
            employee_id=None,
            employee=None,
        )
    return override


def test_document_upload_requires_authentication(client):
    response = client.post(
        "/documents/upload",
        files={"file": ("test.txt", b"sample text", "text/plain")},
    )
    assert response.status_code == 401


@pytest.mark.parametrize("role", ["MANAGER", "EMPLOYEE"])
def test_document_upload_rejects_non_admin(client, set_user, role):
    set_user(role, user_id=2)
    response = client.post(
        "/documents/upload",
        headers=make_headers(2, role),
        files={"file": ("test.txt", b"sample text", "text/plain")},
    )
    assert response.status_code == 403


def test_document_upload_rejects_path_traversal(client, set_user, monkeypatch, tmp_path):
    set_user("ADMIN")
    monkeypatch.setattr(documents, "UPLOAD_DIR", tmp_path)

    response = client.post(
        "/documents/upload",
        headers=make_headers(),
        files={"file": ("../test.txt", b"sample text", "text/plain")},
    )
    assert response.status_code == 400


def test_document_upload_rejects_unsupported_extension(client, set_user, monkeypatch, tmp_path):
    set_user("ADMIN")
    monkeypatch.setattr(documents, "UPLOAD_DIR", tmp_path)

    response = client.post(
        "/documents/upload",
        headers=make_headers(),
        files={"file": ("test.exe", b"sample text", "application/octet-stream")},
    )
    assert response.status_code == 400


def test_document_upload_rejects_duplicate_file(client, set_user, monkeypatch, tmp_path):
    set_user("ADMIN")
    monkeypatch.setattr(documents, "UPLOAD_DIR", tmp_path)
    (tmp_path / "duplicate.txt").write_text("existing")

    response = client.post(
        "/documents/upload",
        headers=make_headers(),
        files={"file": ("duplicate.txt", b"new content", "text/plain")},
    )
    assert response.status_code == 409


def test_document_upload_success(client, set_user, monkeypatch, tmp_path):
    set_user("ADMIN")
    monkeypatch.setattr(documents, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(
        documents.collection,
        "get",
        lambda **kwargs: {"ids": []},
    )
    monkeypatch.setattr(
        documents,
        "ingest_document",
        lambda path: {"filename": "test.txt", "chunks": 2},
    )

    response = client.post(
        "/documents/upload",
        headers=make_headers(),
        files={"file": ("test.txt", b"sample text", "text/plain")},
    )

    assert response.status_code == 200
    assert response.json()["chunks"] == 2
    assert (tmp_path / "test.txt").exists()


def test_document_listing_rejects_non_admin(client, set_user):
    set_user("MANAGER", user_id=2)
    response = client.get("/documents/", headers=make_headers(2, "MANAGER"))
    assert response.status_code == 403


def test_rag_requires_authentication(client):
    response = client.post("/rag/ask", json={"question": "What is company policy?"})
    assert response.status_code == 401


def test_rag_accepts_authenticated_request(client, set_user, monkeypatch):
    set_user("EMPLOYEE", user_id=3)
    monkeypatch.setattr(
        rag,
        "ask_question",
        lambda **kwargs: {"answer": "Test answer"},
    )

    response = client.post(
        "/rag/ask",
        headers=make_headers(3, "EMPLOYEE"),
        json={"question": "What is company policy?"},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "Test answer"


def test_rag_rejects_invalid_top_k(client, set_user):
    set_user("EMPLOYEE", user_id=3)
    response = client.post(
        "/rag/ask",
        headers=make_headers(3, "EMPLOYEE"),
        json={"question": "Test", "top_k": 100},
    )
    assert response.status_code == 422


@pytest.fixture
def conversation_setup():
    db = MagicMock()
    conversation = SimpleNamespace(
        id=101,
        user_id=1,
        title="Test conversation",
    )

    db.query.return_value.filter.return_value.first.return_value = conversation
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

    app.dependency_overrides[get_db] = lambda: db

    with TestClient(app) as test_client:
        yield test_client, db, conversation

    app.dependency_overrides.clear()


def test_conversation_requires_authentication(conversation_setup):
    client, db, conversation = conversation_setup
    response = client.get("/conversations/")
    assert response.status_code == 401


@pytest.mark.parametrize("role", ["assistant", "system"])
def test_conversation_rejects_non_user_messages(conversation_setup, role):
    client, db, conversation = conversation_setup

    response = client.post(
        "/conversations/101/messages",
        headers=make_headers(),
        json={"role": role, "content": "Unauthorized message"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Clients can only submit user messages."


def test_conversation_rejects_unowned_conversation(conversation_setup):
    client, db, conversation = conversation_setup

    db.query.return_value.filter.return_value.first.return_value = None

    response = client.get(
        "/conversations/101",
        headers=make_headers(user_id=2, role="MANAGER"),
    )

    assert response.status_code == 404
