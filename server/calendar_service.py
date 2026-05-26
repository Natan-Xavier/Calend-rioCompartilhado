import uuid
from server.storage_manager import StorageManager


class CalendarService:
    def __init__(self):
        self.storage = StorageManager.get_instance()

    # ── Users ──────────────────────────────────────────────────────────────────

    def create_user(self, data):
        user_id = str(uuid.uuid4())
        user = {
            "id":    user_id,
            "name":  data.get("name"),
            "email": data.get("email"),
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

    # ── Events ─────────────────────────────────────────────────────────────────

    def create_event(self, data):
        existing, _ = self.storage.find_by_name_and_date_global(
            data.get("title", ""), data.get("date", "")
        )
        if existing:
            return None, "conflict"

        event_id = str(uuid.uuid4())
        event = {
            "id":               event_id,
            "title":            data.get("title"),
            "date":             data.get("date"),
            "description":      data.get("description"),
            "created_by":       data.get("created_by", "Desconhecido"),
            "recurrence_id":    data.get("recurrence_id", ""),
            "recurrence_rule":  data.get("recurrence_rule", ""),
        }
        self.storage.save("events", event_id, event)

        self.storage.log_action(
            data.get("created_by", "?"), "CRIOU",
            event["title"], "EVENTO",
            item_date=event.get("date", ""),
            recurrence_id=event.get("recurrence_id", ""),
        )
        return event, None

    def edit_event(self, name, data):
        event, _ = self.storage.find_by_name_global(name)
        if not event:
            return None
        updated = {**event, **data, "id": event["id"]}
        self.storage.update("events", event["id"], updated)
        self.storage.log_action(
            data.get("edited_by", "?"), "EDITOU",
            event["title"], "EVENTO",
            item_date=event.get("date", ""),
        )
        return updated

    def delete_event(self, name, deleted_by="?"):
        event, _ = self.storage.find_by_name_global(name)
        if not event:
            return None
        self.storage.log_action(
            deleted_by, "DELETOU",
            event["title"], "EVENTO",
            item_date=event.get("date", ""),
        )
        self.storage.delete("events", event["id"])
        return {"deleted": name, "created_by": event.get("created_by", "")}

    # ── Reminders ──────────────────────────────────────────────────────────────

    def create_reminder(self, data):
        existing, _ = self.storage.find_by_name_and_date_global(
            data.get("title", ""), data.get("datetime", "")
        )
        if existing:
            return None, "conflict"

        reminder_id = str(uuid.uuid4())
        reminder = {
            "id":              reminder_id,
            "title":           data.get("title"),
            "datetime":        data.get("datetime"),
            "created_by":      data.get("created_by", "Desconhecido"),
            "recurrence_id":   data.get("recurrence_id", ""),
            "recurrence_rule": data.get("recurrence_rule", ""),
        }
        self.storage.save("reminders", reminder_id, reminder)

        self.storage.log_action(
            data.get("created_by", "?"), "CRIOU",
            reminder["title"], "LEMBRETE",
            item_date=reminder.get("datetime", ""),
            recurrence_id=reminder.get("recurrence_id", ""),
        )
        return reminder, None

    def edit_reminder(self, name, data):
        reminder, _ = self.storage.find_by_name_global(name)
        if not reminder:
            return None
        updated = {**reminder, **data, "id": reminder["id"]}
        self.storage.update("reminders", reminder["id"], updated)
        self.storage.log_action(
            data.get("edited_by", "?"), "EDITOU",
            reminder["title"], "LEMBRETE",
            item_date=reminder.get("datetime", ""),
        )
        return updated

    def delete_reminder(self, name, deleted_by="?"):
        reminder, _ = self.storage.find_by_name_global(name)
        if not reminder:
            return None
        self.storage.log_action(
            deleted_by, "DELETOU",
            reminder["title"], "LEMBRETE",
            item_date=reminder.get("datetime", ""),
        )
        self.storage.delete("reminders", reminder["id"])
        return {"deleted": name, "created_by": reminder.get("created_by", "")}

    # ── Agenda ─────────────────────────────────────────────────────────────────

    def get_agenda(self, start, end):
        events    = self.storage.load_by_interval("events",    start, end)
        reminders = self.storage.load_by_interval("reminders", start, end)
        return events, reminders