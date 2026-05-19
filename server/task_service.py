import uuid
from server.storage_manager import StorageManager


class TaskService:
    def __init__(self):
        self.storage = StorageManager.get_instance()

    def add(self, data):
        existing, _ = self.storage.find_by_name_and_date_global(
            data.get("title", ""), data.get("date", "")
        )
        if existing:
            return None, "conflict"
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "title": data.get("title"),
            "description": data.get("description"),
            "date": data.get("date"),
            "done": False,
            "created_by": data.get("created_by", "Desconhecido")
        }
        self.storage.save("tasks", task_id, task)
        return task, None

    def get_all(self):
        return self.storage.load_all("tasks")

    def get_by_interval(self, start, end):
        return self.storage.load_by_interval("tasks", start, end)

    def edit(self, name, data):
        task, _ = self.storage.find_by_name_global(name)
        if not task:
            return None
        updated = {**task, **data, "id": task["id"]}
        self.storage.update("tasks", task["id"], updated)
        return updated

    def delete(self, name):
        task, _ = self.storage.find_by_name_global(name)
        if not task:
            return None
        self.storage.delete("tasks", task["id"])
        return {"deleted": name}