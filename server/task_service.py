import uuid
from server.storage_manager import StorageManager


class TaskService:
    def __init__(self):
        self.storage = StorageManager.get_instance()

    def add(self, data):
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "title": data.get("title"),
            "description": data.get("description"),
            "done": False
        }
        self.storage.save("tasks", task_id, task)
        return task

    def get_all(self):
        return self.storage.load_all("tasks")

    def get_by_interval(self, start, end):
        return self.storage.load_by_interval("tasks", start, end)

    def edit(self, name, data):
        task = self.storage.find_by_name("tasks", name)
        if not task:
            return None
        updated = {**task, **data, "id": task["id"]}
        self.storage.update("tasks", task["id"], updated)
        return updated

    def delete(self, name):
        task = self.storage.find_by_name("tasks", name)
        if not task:
            return None
        self.storage.delete("tasks", task["id"])
        return {"deleted": name}