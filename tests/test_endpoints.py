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


# ── /eventos ───────────────────────────────────────────
def test_create_event(client):
    response = client.post("/eventos", json={
        "title": "Reunião",
        "date": "2026-05-12",
        "description": "Reunião semanal"
    })
    assert response.status_code == 201
    assert response.get_json()["title"] == "Reunião"


def test_edit_event(client):
    client.post("/eventos", json={
        "title": "Reunião",
        "date": "2026-05-12",
        "description": "Reunião semanal"
    })
    response = client.put("/eventos/Reunião", json={
        "description": "Reunião atualizada"
    })
    assert response.status_code == 200
    assert response.get_json()["description"] == "Reunião atualizada"


def test_delete_event(client):
    client.post("/eventos", json={
        "title": "Evento para deletar",
        "date": "2026-05-12",
        "description": "Será deletado"
    })
    response = client.delete("/eventos/Evento para deletar")
    assert response.status_code == 200
    assert response.get_json()["deleted"] == "Evento para deletar"


def test_delete_event_not_found(client):
    response = client.delete("/eventos/Inexistente")
    assert response.status_code == 404


# ── /lembretes ─────────────────────────────────────────
def test_create_reminder(client):
    response = client.post("/lembretes", json={
        "title": "Comprar café",
        "datetime": "2026-05-12T08:00:00"
    })
    assert response.status_code == 201
    assert response.get_json()["title"] == "Comprar café"


def test_edit_reminder(client):
    client.post("/lembretes", json={
        "title": "Comprar café",
        "datetime": "2026-05-12T08:00:00"
    })
    response = client.put("/lembretes/Comprar café", json={
        "datetime": "2026-05-13T09:00:00"
    })
    assert response.status_code == 200
    assert response.get_json()["datetime"] == "2026-05-13T09:00:00"


def test_delete_reminder(client):
    client.post("/lembretes", json={
        "title": "Lembrete para deletar",
        "datetime": "2026-05-12T08:00:00"
    })
    response = client.delete("/lembretes/Lembrete para deletar")
    assert response.status_code == 200


def test_delete_reminder_not_found(client):
    response = client.delete("/lembretes/Inexistente")
    assert response.status_code == 404


# ── /tarefas ───────────────────────────────────────────
def test_add_task(client):
    response = client.post("/tarefas", json={
        "title": "Finalizar relatório",
        "description": "Q2"
    })
    assert response.status_code == 201
    assert response.get_json()["done"] == False


def test_get_tasks(client):
    client.post("/tarefas", json={
        "title": "Tarefa 1",
        "description": "Primeira"
    })
    response = client.get("/tarefas")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
    assert len(response.get_json()) >= 1


def test_edit_task(client):
    client.post("/tarefas", json={
        "title": "Tarefa editável",
        "description": "Original"
    })
    response = client.put("/tarefas/Tarefa editável", json={
        "description": "Atualizada"
    })
    assert response.status_code == 200
    assert response.get_json()["description"] == "Atualizada"


def test_delete_task(client):
    client.post("/tarefas", json={
        "title": "Tarefa para deletar",
        "description": "Será deletada"
    })
    response = client.delete("/tarefas/Tarefa para deletar")
    assert response.status_code == 200
    assert response.get_json()["deleted"] == "Tarefa para deletar"


def test_delete_task_not_found(client):
    response = client.delete("/tarefas/Inexistente")
    assert response.status_code == 404


# ── /agenda ────────────────────────────────────────────
def test_get_agenda(client):
    client.post("/eventos", json={
        "title": "Feira de Carreiras",
        "date": "2026-05-15",
        "description": "Evento anual"
    })
    client.post("/tarefas", json={
        "title": "Entregar projeto",
        "description": "Projeto final",
        "date": "2026-05-20"
    })
    client.post("/lembretes", json={
        "title": "Comprar café",
        "datetime": "2026-05-12T08:00:00"
    })
    response = client.get("/agenda?start=2026-05-01&end=2026-05-31")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(item["type"] == "EVENTO" for item in data)


def test_get_agenda_missing_params(client):
    response = client.get("/agenda")
    assert response.status_code == 400