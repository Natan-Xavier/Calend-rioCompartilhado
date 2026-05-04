class StorageManager:
    _instance = None

    def __init__(self):
        self.users = {}
        self.events = {}
        self.reminders = {}
        self.tasks = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = StorageManager()
        return cls._instance

    def save(self, resource, key, data):
        getattr(self, resource)[key] = data
        return True

    def load(self, resource, key):
        return getattr(self, resource).get(key)

    def load_all(self, resource):
        return list(getattr(self, resource).values())

    def delete(self, resource, key):
        if key in getattr(self, resource):
            del getattr(self, resource)[key]
            return True
        return False

    def exists(self, resource, key):
        return key in getattr(self, resource)