import json
import os
import uuid
from datetime import datetime


class StorageManager:
    _instance = None
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

    def __init__(self):
        os.makedirs(self.DATA_DIR, exist_ok=True)
        self.resources = ["users", "events", "reminders", "tasks", "history"]
        for resource in self.resources:
            if not os.path.exists(self._path(resource)):
                self._write(resource, {})

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = StorageManager()
        return cls._instance

    def _path(self, resource):
        return os.path.join(self.DATA_DIR, f"{resource}.json")

    def _read(self, resource):
        path = self._path(resource)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write(self, resource, data):
        with open(self._path(resource), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save(self, resource, key, data):
        store = self._read(resource)
        store[key] = data
        self._write(resource, store)
        return True

    def load_all(self, resource):
        return list(self._read(resource).values())

    def load_by_interval(self, resource, start, end):
        result = []
        for item in self._read(resource).values():
            item_date = item.get("date") or item.get("datetime", "")
            if item_date:
                item_date = item_date[:10]
                if start <= item_date <= end:
                    result.append(item)
        return result

    def find_by_name_global(self, name):
        for resource in self.resources:
            if resource == "history":
                continue
            for item in self._read(resource).values():
                if item.get("title", "").lower() == name.lower():
                    return item, resource
        return None, None

    def find_by_name_and_date_global(self, name, date_str):
        """Returns (item, resource) if same title AND same date already exists."""
        for resource in ["events", "reminders", "tasks"]:
            for item in self._read(resource).values():
                item_date = (item.get("date") or item.get("datetime", ""))[:10]
                if (item.get("title", "").lower() == name.lower() and
                        item_date == date_str[:10]):
                    return item, resource
        return None, None

    def update(self, resource, key, data):
        store = self._read(resource)
        if key in store:
            store[key] = data
            self._write(resource, store)
            return True
        return False

    def delete(self, resource, key):
        store = self._read(resource)
        if key in store:
            del store[key]
            self._write(resource, store)
            return True
        return False

    def exists(self, resource, key):
        return key in self._read(resource)

    def log_action(self, user, action, item_title, item_type,
                   item_date="", recurrence_id=""):
        """
        Log an action to history.
        If recurrence_id is set, only logs ONCE for the whole series
        (deduplicates by recurrence_id + action).
        """
        if recurrence_id:
            for entry in self._read("history").values():
                if (entry.get("recurrence_id") == recurrence_id and
                        entry.get("action") == action):
                    return None  # already logged for this series

        entry_id = str(uuid.uuid4())
        entry = {
            "id":            entry_id,
            "timestamp":     datetime.now().strftime("%d/%m/%Y %H:%M"),
            "user":          user,
            "action":        action,
            "item":          item_title,
            "type":          item_type,
            "item_date":     item_date[:10] if item_date else "",
            "recurrence_id": recurrence_id,
        }
        self.save("history", entry_id, entry)
        return entry

    def get_history(self):
        entries = self.load_all("history")
        return sorted(entries, key=lambda x: x.get("timestamp", ""), reverse=True)