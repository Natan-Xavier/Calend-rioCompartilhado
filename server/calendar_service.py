import uuid
from server.storage_manager import StorageManager


class CalendarService:
    def __init__(self):
        self.storage = StorageManager.get_instance()

    def create_user(self, data):
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "name": data.get("name"),
            "email": data.get("email")
        }
        self.storage.save("users", user_id, user)
        return user

    def create_event(self, data):
        event_id = str(uuid.uuid4())
        event = {
            "id": event_id,
            "title": data.get("title"),
            "date": data.get("date"),
            "description": data.get("description")
        }
        self.storage.save("events", event_id, event)
        return event

    def create_reminder(self, data):
        reminder_id = str(uuid.uuid4())
        reminder = {
            "id": reminder_id,
            "title": data.get("title"),
            "datetime": data.get("datetime")
        }
        self.storage.save("reminders", reminder_id, reminder)
        return reminder