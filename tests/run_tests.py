import sys
import os
import json
import threading
import time
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.app import app

BASE_URL = "http://127.0.0.1:5000"


def start_server():
    app.run(debug=False, use_reloader=False)


def print_response(method, endpoint, response):
    print(f"\n{'='*50}")
    print(f"Testing {method} {endpoint}")
    print(f"→ Status: {response.status_code}")
    print(f"→ Response: {json.dumps(response.json(), indent=2)}")


def run():
    # start server in background thread
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()
    time.sleep(1)  # wait for server to start

    print("\n🚀 SharedCalendar — Endpoint Tests\n")

    # POST /usuarios
    r = requests.post(f"{BASE_URL}/usuarios", json={
        "name": "John Doe",
        "email": "john@email.com"
    })
    print_response("POST", "/usuarios", r)

    # POST /eventos
    r = requests.post(f"{BASE_URL}/eventos", json={
        "title": "Team Meeting",
        "date": "2026-05-10",
        "description": "Weekly sync"
    })
    print_response("POST", "/eventos", r)

    # POST /lembretes
    r = requests.post(f"{BASE_URL}/lembretes", json={
        "title": "Buy groceries",
        "datetime": "2026-05-10T08:00:00"
    })
    print_response("POST", "/lembretes", r)

    # POST /tarefas
    r = requests.post(f"{BASE_URL}/tarefas", json={
        "title": "Finish report",
        "description": "Q2 report"
    })
    print_response("POST", "/tarefas", r)
    task_id = r.json()["id"]

    # GET /tarefas
    r = requests.get(f"{BASE_URL}/tarefas")
    print_response("GET", "/tarefas", r)

    # DELETE /tarefas/<id>
    r = requests.delete(f"{BASE_URL}/tarefas/{task_id}")
    print_response("DELETE", f"/tarefas/{task_id}", r)

    print(f"\n{'='*50}")
    print("✅ All endpoints tested successfully!")


if __name__ == "__main__":
    run()