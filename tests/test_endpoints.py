import pytest
from server.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── /usuarios ──────────────────────────────────────────
def test_create_user(client):
    response = client.post("/usuarios", json={
        "name": "John Doe",
        "email": "john@email.com"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["name"] == "John Doe"
    assert data["email"] == "john@email.com"


# ── /eventos ───────────────────────────────────────────
def test_create_event(client):
    response = client.post("/eventos", json={
        "title": "Team Meeting",
        "date": "2026-05-10",
        "description": "Weekly sync"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["title"] == "Team Meeting"


# ── /lembretes ─────────────────────────────────────────
def test_create_reminder(client):
    response = client.post("/lembretes", json={
        "title": "Buy groceries",
        "datetime": "2026-05-10T08:00:00"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["title"] == "Buy groceries"


# ── /tarefas ───────────────────────────────────────────
def test_add_task(client):
    response = client.post("/tarefas", json={
        "title": "Finish report",
        "description": "Q2 report"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["title"] == "Finish report"
    assert data["done"] == False


def test_get_tasks(client):
    client.post("/tarefas", json={
        "title": "Task 1",
        "description": "First task"
    })
    response = client.get("/tarefas")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_delete_task(client):
    post = client.post("/tarefas", json={
        "title": "Task to delete",
        "description": "Will be deleted"
    })
    task_id = post.get_json()["id"]

    response = client.delete(f"/tarefas/{task_id}")
    assert response.status_code == 200
    assert response.get_json()["deleted"] == task_id


def test_delete_task_not_found(client):
    response = client.delete("/tarefas/nonexistent-id")
    assert response.status_code == 404