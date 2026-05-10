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

    def edit_event(self, name, data):
        event = self.storage.find_by_name("events", name)
        if not event:
            return None
        updated = {**event, **data, "id": event["id"]}
        self.storage.update("events", event["id"], updated)
        return updated

    def delete_event(self, name):
        event = self.storage.find_by_name("events", name)
        if not event:
            return None
        self.storage.delete("events", event["id"])
        return {"deleted": name}

    def create_reminder(self, data):
        reminder_id = str(uuid.uuid4())
        reminder = {
            "id": reminder_id,
            "title": data.get("title"),
            "datetime": data.get("datetime")
        }
        self.storage.save("reminders", reminder_id, reminder)
        return reminder

    def edit_reminder(self, name, data):
        reminder = self.storage.find_by_name("reminders", name)
        if not reminder:
            return None
        updated = {**reminder, **data, "id": reminder["id"]}
        self.storage.update("reminders", reminder["id"], updated)
        return updated

    def delete_reminder(self, name):
        reminder = self.storage.find_by_name("reminders", name)
        if not reminder:
            return None
        self.storage.delete("reminders", reminder["id"])
        return {"deleted": name}

    def get_agenda(self, start, end):
        events = self.storage.load_by_interval("events", start, end)
        reminders = self.storage.load_by_interval("reminders", start, end)
        return events, reminders