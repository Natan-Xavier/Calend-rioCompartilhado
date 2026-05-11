from flask import Flask, request, jsonify
from server.calendar_service import CalendarService
from server.task_service import TaskService

app = Flask(__name__)

calendar_service = CalendarService()
task_service = TaskService()


# ── /usuarios ──────────────────────────────────────────
@app.route("/usuarios", methods=["POST"])
def create_user():
    data = request.get_json()
    result = calendar_service.create_user(data)
    return jsonify(result), 201


# ── /eventos ───────────────────────────────────────────
@app.route("/eventos", methods=["POST"])
def create_event():
    data = request.get_json()
    result, error = calendar_service.create_event(data)
    if error == "conflict":
        return jsonify({"error": f"Já existe um item com o nome '{data.get('title')}'"}), 409
    return jsonify(result), 201

@app.route("/eventos/<name>", methods=["PUT"])
def edit_event(name):
    data = request.get_json()
    result = calendar_service.edit_event(name, data)
    if result is None:
        return jsonify({"error": "Evento não encontrado"}), 404
    return jsonify(result), 200


@app.route("/eventos/<name>", methods=["DELETE"])
def delete_event(name):
    result = calendar_service.delete_event(name)
    if result is None:
        return jsonify({"error": "Evento não encontrado"}), 404
    return jsonify(result), 200

@app.route("/find/<name>", methods=["GET"])
def find_by_name(name):
    item, resource = calendar_service.storage.find_by_name_global(name)
    if item is None:
        return jsonify({"error": "Item não encontrado"}), 404
    return jsonify({"item": item, "resource": resource}), 200


# ── /lembretes ─────────────────────────────────────────
@app.route("/lembretes", methods=["POST"])
def create_reminder():
    data = request.get_json()
    result, error = calendar_service.create_reminder(data)
    if error == "conflict":
        return jsonify({"error": f"Já existe um item com o nome '{data.get('title')}'"}), 409
    return jsonify(result), 201


@app.route("/lembretes/<name>", methods=["PUT"])
def edit_reminder(name):
    data = request.get_json()
    result = calendar_service.edit_reminder(name, data)
    if result is None:
        return jsonify({"error": "Lembrete não encontrado"}), 404
    return jsonify(result), 200


@app.route("/lembretes/<name>", methods=["DELETE"])
def delete_reminder(name):
    result = calendar_service.delete_reminder(name)
    if result is None:
        return jsonify({"error": "Lembrete não encontrado"}), 404
    return jsonify(result), 200


# ── /tarefas ───────────────────────────────────────────
@app.route("/tarefas", methods=["POST"])
def add_task():
    data = request.get_json()
    result, error = task_service.add(data)
    if error == "conflict":
        return jsonify({"error": f"Já existe um item com o nome '{data.get('title')}'"}), 409
    return jsonify(result), 201


@app.route("/tarefas", methods=["GET"])
def get_tasks():
    result = task_service.get_all()
    return jsonify(result), 200


@app.route("/tarefas/<name>", methods=["PUT"])
def edit_task(name):
    data = request.get_json()
    result = task_service.edit(name, data)
    if result is None:
        return jsonify({"error": "Tarefa não encontrada"}), 404
    return jsonify(result), 200


@app.route("/tarefas/<name>", methods=["DELETE"])
def delete_task(name):
    result = task_service.delete(name)
    if result is None:
        return jsonify({"error": "Tarefa não encontrada"}), 404
    return jsonify(result), 200


# ── /agenda ────────────────────────────────────────────
@app.route("/agenda", methods=["GET"])
def get_agenda():
    start = request.args.get("start")
    end = request.args.get("end")
    if not start or not end:
        return jsonify({"error": "Parâmetros start e end são obrigatórios"}), 400

    events, reminders = calendar_service.get_agenda(start, end)
    tasks = task_service.get_by_interval(start, end)

    agenda = []
    for e in events:
        agenda.append({**e, "type": "EVENTO"})
    for r in reminders:
        agenda.append({**r, "type": "LEMBRETE"})
    for t in tasks:
        agenda.append({**t, "type": "TAREFA"})

    agenda.sort(key=lambda x: x.get("date") or x.get("datetime", "")[:10])

    return jsonify(agenda), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)