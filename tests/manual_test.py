import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def print_response(method, endpoint, response):
    print(f"\n{'='*50}")
    print(f"{method} {endpoint}")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2)}")

print("\n🚀 Testando endpoints do SharedCalendar\n")

# POST /usuarios
print_response("POST", "/usuarios", requests.post(f"{BASE_URL}/usuarios", json={
    "name": "João Silva",
    "email": "joao@email.com"
}))

# POST /eventos
print_response("POST", "/eventos", requests.post(f"{BASE_URL}/eventos", json={
    "title": "Reunião",
    "date": "2026-05-12",
    "description": "Reunião semanal"
}))

# POST /lembretes
print_response("POST", "/lembretes", requests.post(f"{BASE_URL}/lembretes", json={
    "title": "Comprar café",
    "datetime": "2026-05-12T08:00:00"
}))

# POST /tarefas
r = requests.post(f"{BASE_URL}/tarefas", json={
    "title": "Finalizar relatório",
    "description": "Relatório Q2"
})
print_response("POST", "/tarefas", r)
task_id = r.json()["id"]

# GET /tarefas
print_response("GET", "/tarefas", requests.get(f"{BASE_URL}/tarefas"))

# DELETE /tarefas/<id>
print_response("DELETE", f"/tarefas/{task_id}", requests.delete(f"{BASE_URL}/tarefas/{task_id}"))

print(f"\n{'='*50}")
print("✅ Todos os endpoints testados!")