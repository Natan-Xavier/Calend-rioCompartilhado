from flask import Flask, request, jsonify
from server.calendar_service import CalendarService
from server.task_service import TaskService

app = Flask(__name__)

calendar_service = CalendarService()
task_service = TaskService()


@app.route("/usuarios", methods=["POST"])
def create_user():
    data = request.get_json()
    result = calendar_service.create_user(data)
    return jsonify(result), 201


@app.route("/eventos", methods=["POST"])
def create_event():
    data = request.get_json()
    result = calendar_service.create_event(data)
    return jsonify(result), 201


@app.route("/lembretes", methods=["POST"])
def create_reminder():
    data = request.get_json()
    result = calendar_service.create_reminder(data)
    return jsonify(result), 201


@app.route("/tarefas", methods=["POST"])
def add_task():
    data = request.get_json()
    result = task_service.add(data)
    return jsonify(result), 201


@app.route("/tarefas", methods=["GET"])
def get_tasks():
    result = task_service.get_all()
    return jsonify(result), 200


@app.route("/tarefas/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    result = task_service.delete(task_id)
    if result is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True)