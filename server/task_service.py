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

    def delete(self, task_id):
        if not self.storage.exists("tasks", task_id):
            return None
        self.storage.delete("tasks", task_id)
        return {"deleted": task_id}