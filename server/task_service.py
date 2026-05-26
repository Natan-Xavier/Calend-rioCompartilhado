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
            "id":              task_id,
            "title":           data.get("title"),
            "description":     data.get("description"),
            "date":            data.get("date"),
            "done":            False,
            "created_by":      data.get("created_by", "Desconhecido"),
            # FIX: persist recurrence fields so EditDialog shows the checkbox
            "recurrence_id":   data.get("recurrence_id", ""),
            "recurrence_rule": data.get("recurrence_rule", ""),
        }
        self.storage.save("tasks", task_id, task)

        self.storage.log_action(
            data.get("created_by", "?"), "CRIOU",
            task["title"], "TAREFA",
            item_date=task.get("date", ""),
            # dedup: only log once per recurrence series
            recurrence_id=task.get("recurrence_id", ""),
        )
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
        self.storage.log_action(
            data.get("edited_by", "?"), "EDITOU",
            task["title"], "TAREFA",
            item_date=task.get("date", ""),
        )
        return updated

    def delete(self, name, deleted_by="?"):
        task, _ = self.storage.find_by_name_global(name)
        if not task:
            return None
        self.storage.log_action(
            deleted_by, "DELETOU",
            task["title"], "TAREFA",
            item_date=task.get("date", ""),
        )
        self.storage.delete("tasks", task["id"])
        return {"deleted": name, "created_by": task.get("created_by", "")}