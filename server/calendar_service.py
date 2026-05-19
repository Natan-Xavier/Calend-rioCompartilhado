import uuid
from server.storage_manager import StorageManager


class CalendarService:
    def __init__(self):
        self.storage = StorageManager.get_instance()

    # ── Usuários ───────────────────────────────────────────
    def create_user(self, data):
        user_id = str(uuid.uuid4())
        user    = {
            "id":    user_id,
            "name":  data.get("name"),
            "email": data.get("email")
        }
        self.storage.save("users", user_id, user)
        return user, None

    def get_users(self):
        return self.storage.load_all("users")

    def delete_user(self, user_id):
        if not self.storage.exists("users", user_id):
            return None
        self.storage.delete("users", user_id)
        return {"deleted": user_id}

    # ── Eventos ────────────────────────────────────────────
    def create_event(self, data):
        # Validate: same name + same date = conflict
        existing, _ = self.storage.find_by_name_and_date_global(
            data.get("title", ""), data.get("date", "")
        )
        if existing:
            return None, "conflict"
        event_id = str(uuid.uuid4())
        event    = {
            "id":          event_id,
            "title":       data.get("title"),
            "date":        data.get("date"),
            "description": data.get("description"),
            "created_by":  data.get("created_by", "Desconhecido"),
        }
        # Preserve recurrence fields if present
        if data.get("recurrence_id"):
            event["recurrence_id"]   = data["recurrence_id"]
            event["recurrence_rule"] = data.get("recurrence_rule")
        self.storage.save("events", event_id, event)
        return event, None

    def edit_event(self, name, data):
        event, _ = self.storage.find_by_name_global(name)
        if not event:
            return None
        updated = {**event, **data, "id": event["id"]}
        self.storage.update("events", event["id"], updated)
        return updated

    def delete_event(self, name):
        event, _ = self.storage.find_by_name_global(name)
        if not event:
            return None
        self.storage.delete("events", event["id"])
        return {"deleted": name}

    # ── Lembretes ──────────────────────────────────────────
    def create_reminder(self, data):
        existing, _ = self.storage.find_by_name_and_date_global(
            data.get("title", ""), data.get("datetime", "")
        )
        if existing:
            return None, "conflict"
        reminder_id = str(uuid.uuid4())
        reminder    = {
            "id":         reminder_id,
            "title":      data.get("title"),
            "datetime":   data.get("datetime"),
            "created_by": data.get("created_by", "Desconhecido"),
        }
        if data.get("recurrence_id"):
            reminder["recurrence_id"]   = data["recurrence_id"]
            reminder["recurrence_rule"] = data.get("recurrence_rule")
        self.storage.save("reminders", reminder_id, reminder)
        return reminder, None

    def edit_reminder(self, name, data):
        reminder, _ = self.storage.find_by_name_global(name)
        if not reminder:
            return None
        updated = {**reminder, **data, "id": reminder["id"]}
        self.storage.update("reminders", reminder["id"], updated)
        return updated

    def delete_reminder(self, name):
        reminder, _ = self.storage.find_by_name_global(name)
        if not reminder:
            return None
        self.storage.delete("reminders", reminder["id"])
        return {"deleted": name}

    # ── Agenda ─────────────────────────────────────────────
    def get_agenda(self, start, end):
        events    = self.storage.load_by_interval("events",    start, end)
        reminders = self.storage.load_by_interval("reminders", start, end)
        return events, reminders