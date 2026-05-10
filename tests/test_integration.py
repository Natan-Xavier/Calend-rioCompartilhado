import pytest
import threading
import time
from client.calendar_proxy import CalendarProxy
from server.app import app


@pytest.fixture(scope="module")
def server():
    """Sobe o servidor em background antes dos testes"""
    thread = threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False),
        daemon=True
    )
    thread.start()
    time.sleep(1)
    yield


@pytest.fixture(scope="module")
def proxy(server):
    """Instancia o proxy apontando para o servidor de teste"""
    return CalendarProxy("http://127.0.0.1:5001")


# ── Fluxo de usuário ───────────────────────────────────
def test_create_user(proxy):
    data, status = proxy.create_user("João Silva", "joao@email.com")
    assert status == 201
    assert data["name"] == "João Silva"
    assert data["email"] == "joao@email.com"
    assert "id" in data


# ── Fluxo de evento ────────────────────────────────────
def test_create_event(proxy):
    data, status = proxy.create_event("Reunião Semanal", "2026-05-15", "Reunião do time")
    assert status == 201
    assert data["title"] == "Reunião Semanal"


def test_edit_event(proxy):
    proxy.create_event("Evento Editável", "2026-05-16", "Original")
    data, status = proxy.edit_event("Evento Editável", {"description": "Atualizado"})
    assert status == 200
    assert data["description"] == "Atualizado"


def test_delete_event(proxy):
    proxy.create_event("Evento para Deletar", "2026-05-17", "Será deletado")
    data, status = proxy.delete_event("Evento para Deletar")
    assert status == 200
    assert data["deleted"] == "Evento para Deletar"


def test_delete_event_not_found(proxy):
    data, status = proxy.delete_event("Evento Inexistente")
    assert status == 404


# ── Fluxo de lembrete ──────────────────────────────────
def test_create_reminder(proxy):
    data, status = proxy.create_reminder("Comprar café", "2026-05-15T08:00:00")
    assert status == 201
    assert data["title"] == "Comprar café"


def test_edit_reminder(proxy):
    proxy.create_reminder("Lembrete Editável", "2026-05-16T08:00:00")
    data, status = proxy.edit_reminder("Lembrete Editável", {"datetime": "2026-05-17T09:00:00"})
    assert status == 200
    assert data["datetime"] == "2026-05-17T09:00:00"


def test_delete_reminder(proxy):
    proxy.create_reminder("Lembrete para Deletar", "2026-05-18T08:00:00")
    data, status = proxy.delete_reminder("Lembrete para Deletar")
    assert status == 200
    assert data["deleted"] == "Lembrete para Deletar"


def test_delete_reminder_not_found(proxy):
    data, status = proxy.delete_reminder("Lembrete Inexistente")
    assert status == 404


# ── Fluxo de tarefa ────────────────────────────────────
def test_add_task(proxy):
    data, status = proxy.add_task("Finalizar relatório", "Relatório Q2")
    assert status == 201
    assert data["title"] == "Finalizar relatório"
    assert data["done"] == False


def test_get_tasks(proxy):
    proxy.add_task("Tarefa Listável", "Para listar")
    data, status = proxy.get_tasks()
    assert status == 200
    assert isinstance(data, list)
    titles = [t["title"] for t in data]
    assert "Tarefa Listável" in titles


def test_edit_task(proxy):
    proxy.add_task("Tarefa Editável", "Original")
    data, status = proxy.edit_task("Tarefa Editável", {"description": "Atualizada"})
    assert status == 200
    assert data["description"] == "Atualizada"


def test_delete_task(proxy):
    proxy.add_task("Tarefa para Deletar", "Será deletada")
    data, status = proxy.delete_task("Tarefa para Deletar")
    assert status == 200
    assert data["deleted"] == "Tarefa para Deletar"


def test_delete_task_not_found(proxy):
    data, status = proxy.delete_task("Tarefa Inexistente")
    assert status == 404


# ── Fluxo completo da agenda ───────────────────────────
def test_agenda_shows_all_types(proxy):
    proxy.create_event("Feira de Carreiras", "2026-06-10", "Evento anual")
    proxy.create_reminder("Reunião às 9h", "2026-06-15T09:00:00")
    proxy.add_task("Entregar projeto", "Projeto final")

    data, status = proxy.get_agenda("2026-06-01", "2026-06-30")
    assert status == 200
    assert isinstance(data, list)
    types = [item["type"] for item in data]
    assert "EVENTO" in types
    assert "LEMBRETE" in types


def test_agenda_empty_interval(proxy):
    data, status = proxy.get_agenda("2000-01-01", "2000-01-02")
    assert status == 200
    assert data == []


def test_agenda_missing_params(proxy):
    import requests
    response = requests.get("http://127.0.0.1:5001/agenda")
    assert response.status_code == 400


def test_agenda_ordered_by_date(proxy):
    proxy.create_event("Evento Z", "2026-07-20", "Último")
    proxy.create_event("Evento A", "2026-07-05", "Primeiro")
    proxy.create_reminder("Lembrete M", "2026-07-10T08:00:00")

    data, status = proxy.get_agenda("2026-07-01", "2026-07-31")
    assert status == 200
    dates = [item.get("date") or item.get("datetime", "")[:10] for item in data]
    assert dates == sorted(dates)