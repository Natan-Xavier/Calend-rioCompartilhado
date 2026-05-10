import requests
import json

BASE_URL = "http://127.0.0.1:5000"


def print_response(method, endpoint, response):
    print(f"\n{'='*50}")
    print(f"{method} {endpoint}")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


print("\n🚀 SharedCalendar — Teste Manual dos Endpoints\n")

# POST /usuarios
print_response("POST", "/usuarios", requests.post(f"{BASE_URL}/usuarios", json={
    "name": "João Silva",
    "email": "joao@email.com"
}))

# POST /eventos
print_response("POST", "/eventos", requests.post(f"{BASE_URL}/eventos", json={
    "title": "Feira de Carreiras",
    "date": "2026-05-15",
    "description": "Evento anual"
}))

# PUT /eventos/<name>
print_response("PUT", "/eventos/Feira de Carreiras", requests.put(
    f"{BASE_URL}/eventos/Feira de Carreiras", json={
        "description": "Evento anual atualizado"
    }
))

# POST /lembretes
print_response("POST", "/lembretes", requests.post(f"{BASE_URL}/lembretes", json={
    "title": "Comprar café",
    "datetime": "2026-05-12T08:00:00"
}))

# PUT /lembretes/<name>
print_response("PUT", "/lembretes/Comprar café", requests.put(
    f"{BASE_URL}/lembretes/Comprar café", json={
        "datetime": "2026-05-13T09:00:00"
    }
))

# POST /tarefas
print_response("POST", "/tarefas", requests.post(f"{BASE_URL}/tarefas", json={
    "title": "Finalizar relatório",
    "description": "Relatório Q2"
}))

# PUT /tarefas/<name>
print_response("PUT", "/tarefas/Finalizar relatório", requests.put(
    f"{BASE_URL}/tarefas/Finalizar relatório", json={
        "description": "Relatório Q2 atualizado"
    }
))

# GET /tarefas
print_response("GET", "/tarefas", requests.get(f"{BASE_URL}/tarefas"))

# GET /agenda
print_response("GET", "/agenda?start=2026-05-01&end=2026-05-31",
    requests.get(f"{BASE_URL}/agenda?start=2026-05-01&end=2026-05-31"))

# DELETE /eventos/<name>
print_response("DELETE", "/eventos/Feira de Carreiras",
    requests.delete(f"{BASE_URL}/eventos/Feira de Carreiras"))

# DELETE /lembretes/<name>
print_response("DELETE", "/lembretes/Comprar café",
    requests.delete(f"{BASE_URL}/lembretes/Comprar café"))

# DELETE /tarefas/<name>
print_response("DELETE", "/tarefas/Finalizar relatório",
    requests.delete(f"{BASE_URL}/tarefas/Finalizar relatório"))

print(f"\n{'='*50}")
print("✅ Todos os endpoints testados!")