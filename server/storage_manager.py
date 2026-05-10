import json
import os


class StorageManager:
    _instance = None
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

    def __init__(self):
        os.makedirs(self.DATA_DIR, exist_ok=True)
        self.resources = ["users", "events", "reminders", "tasks"]
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
        with open(self._path(resource), "r", encoding="utf-8") as f:
            return json.load(f)

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
            item_date = item.get("date") or item.get("datetime")
            if item_date:
                item_date = item_date[:10]
                if start <= item_date <= end:
                    result.append(item)
        return result

    def find_by_name(self, resource, name):
        for item in self._read(resource).values():
            if item.get("title") == name:
                return item
        return None

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