from types import SimpleNamespace
from unittest.mock import MagicMock


import pytest  # ty: ignore[unresolved-import]
from fastapi.testclient import TestClient

from app.main import app
from app.api import agent as agent_api
from app.core.security import create_access_token
from app.core.dependencies import get_current_user
from app.db.database import get_db


def make_token(user_id=1, role="ADMIN"):
    return create_access_token(
        user_id=user_id,
        role=role
    )
    return jwt.encode(  # noqa: F821
        payload,  # noqa: F821
        JWT_SECRET,  # noqa: F821
        algorithm=JWT_ALGORITHM,  # noqa: F821
    )


@pytest.fixture
def api_setup(monkeypatch):
    db = MagicMock()

    conversation = SimpleNamespace(
        id=101,
        user_id=1,
        title="",
        updated_at=None,
    )

    db.query.return_value.filter.return_value.first.return_value = conversation

    saved_messages = []

    monkeypatch.setattr(
        agent_api,
        "get_conversation_messages",
        lambda **kwargs: [
            SimpleNamespace(role="user", content="Tell me about leave policies."),
            SimpleNamespace(role="assistant", content="I can help with that."),
        ],
    )

    def fake_save_message(
    db,
    conversation_id,
    role,
    content,
    sources=None
):
        saved_messages.append({
    "conversation_id": conversation_id,
    "role": role,
    "content": content,
    "sources": sources
})

    monkeypatch.setattr(
        agent_api,
        "save_message",
        fake_save_message,
    )

    monkeypatch.setattr(
        agent_api,
        "execute_agent",
        lambda **kwargs: {
            "answer": "Employees receive 20 days of annual leave.",
            "intent": "RAG",
            "tool": "rag_search",
            "tool_result": {"answer": "20 days"},
        },
    )

    app.dependency_overrides[get_db] = lambda: db

    with TestClient(app) as client:
        yield client, db, conversation, saved_messages

    app.dependency_overrides.clear()


def test_agent_api_successful_question(api_setup):
    client, db, conversation, saved_messages = api_setup

    response = client.post(
        "/agent/ask",
        headers={
            "Authorization": f"Bearer {make_token(user_id=1)}"
        },
        json={
            "question": "How many annual leave days do employees receive?",
            "conversation_id": 101,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["conversation_id"] == 101
    assert data["intent"] == "RAG"
    assert data["tool"] == "rag_search"
    assert "20 days" in data["answer"]

    assert len(saved_messages) == 2
    assert saved_messages[0]["role"] == "user"
    assert saved_messages[1]["role"] == "assistant"

    assert conversation.title == "How many annual leave days do employees receive?"


def test_agent_api_requires_authentication(api_setup):
    client, db, conversation, saved_messages = api_setup

    response = client.post(
        "/agent/ask",
        json={
            "question": "Hello",
            "conversation_id": 101,
        },
    )

    assert response.status_code == 401
    assert saved_messages == []


def test_agent_api_rejects_missing_or_unowned_conversation(api_setup, monkeypatch):
    client, db, conversation, saved_messages = api_setup

    monkeypatch.setattr(
        agent_api,
        "get_conversation_messages",
        lambda **kwargs: None,
    )

    response = client.post(
        "/agent/ask",
        headers={
            "Authorization": f"Bearer {make_token(user_id=2)}"
        },
        json={
            "question": "Show my previous conversation",
            "conversation_id": 101,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found"
    assert saved_messages == []

def test_agent_api_passes_conversation_history(api_setup, monkeypatch):
    client, db, conversation, saved_messages = api_setup

    captured = {}

    def fake_execute_agent(
    question,
    conversation_history,
    user_id,
    db
):
        captured["question"] = question
        captured["history"] = conversation_history

        return {
            "answer": "20 days",
            "intent": "RAG",
            "tool": "rag_search",
            "tool_result": {"answer": "20 days"},
        }

    monkeypatch.setattr(
        agent_api,
        "execute_agent",
        fake_execute_agent,
    )

    response = client.post(
        "/agent/ask",
        headers={
            "Authorization": f"Bearer {make_token(user_id=1)}"
        },
        json={
            "question": "How many days?",
            "conversation_id": 101,
        },
    )

    assert response.status_code == 200
    assert captured["question"] == "How many days?"

    assert len(captured["history"]) == 2
    assert captured["history"][0]["role"] == "user"
    assert "leave policies" in captured["history"][0]["content"]
    assert captured["history"][1]["role"] == "assistant"


def test_agent_api_preserves_existing_conversation_title(api_setup):
    client, db, conversation, saved_messages = api_setup

    conversation.title = "Employee Leave Policy"

    response = client.post(
        "/agent/ask",
        headers={
            "Authorization": f"Bearer {make_token(user_id=1)}"
        },
        json={
            "question": "How many days?",
            "conversation_id": 101,
        },
    )

    assert response.status_code == 200
    assert conversation.title == "Employee Leave Policy"

def test_agent_failure_rolls_back_transaction(api_setup, monkeypatch):
    client, db, conversation, saved_messages = api_setup

    def failing_agent(**kwargs):
        raise RuntimeError("Simulated agent failure")

    monkeypatch.setattr(
        agent_api,
        "execute_agent",
        failing_agent,
    )

    with pytest.raises(RuntimeError, match="Simulated agent failure"):
        client.post(
            "/agent/ask",
            headers={
                "Authorization": f"Bearer {make_token(user_id=1)}"
            },
            json={
                "question": "How many annual leave days?",
                "conversation_id": 101,
            },
        )

    # Only the user message was staged before the agent failed.
    assert len(saved_messages) == 1
    assert saved_messages[0]["role"] == "user"

    # The transaction must be rolled back, not committed.
    db.rollback.assert_called_once()
    db.commit.assert_not_called()
    
        