import requests


class CalendarProxy:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        if not base_url.startswith("http"):
            base_url = f"http://{base_url}:5000"
        self.base_url     = base_url
        self.current_user = "Desconhecido"

    def _request(self, method, endpoint, data=None, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, json=data, params=params)
            return response.json(), response.status_code
        except requests.exceptions.ConnectionError:
            print("❌ Erro: servidor não está rodando!")
            return None, 503

    # ── Usuarios ───────────────────────────────────────────────────────────────

    def create_user(self, name, email):
        return self._request("POST", "/usuarios", {"name": name, "email": email})

    def get_users(self):
        return self._request("GET", "/usuarios")

    def delete_user(self, user_id):
        return self._request("DELETE", f"/usuarios/{user_id}")

    # ── Eventos ────────────────────────────────────────────────────────────────

    def create_event(self, title, date, description, created_by=None, extra=None):
        data = {
            "title":       title,
            "date":        date,
            "description": description,
            "created_by":  created_by or self.current_user,
        }
        if extra:
            data.update(extra)
        return self._request("POST", "/eventos", data)

    def edit_event(self, name, data):
        if "edited_by" not in data:
            data["edited_by"] = self.current_user
        return self._request("PUT", f"/eventos/{name}", data)

    def delete_event(self, name):
        return self._request("DELETE", f"/eventos/{name}",
                             params={"deleted_by": self.current_user})

    # ── Lembretes ──────────────────────────────────────────────────────────────

    def create_reminder(self, title, datetime, created_by=None, extra=None):
        data = {
            "title":      title,
            "datetime":   datetime,
            "created_by": created_by or self.current_user,
        }
        if extra:
            data.update(extra)
        return self._request("POST", "/lembretes", data)

    def edit_reminder(self, name, data):
        if "edited_by" not in data:
            data["edited_by"] = self.current_user
        return self._request("PUT", f"/lembretes/{name}", data)

    def delete_reminder(self, name):
        return self._request("DELETE", f"/lembretes/{name}",
                             params={"deleted_by": self.current_user})

    # ── Tarefas ────────────────────────────────────────────────────────────────

    def add_task(self, title, description, date, created_by=None, extra=None):
        data = {
            "title":       title,
            "description": description,
            "date":        date,
            "created_by":  created_by or self.current_user,
        }
        if extra:
            data.update(extra)
        return self._request("POST", "/tarefas", data)

    def edit_task(self, name, data):
        if "edited_by" not in data:
            data["edited_by"] = self.current_user
        return self._request("PUT", f"/tarefas/{name}", data)

    def delete_task(self, name):
        return self._request("DELETE", f"/tarefas/{name}",
                             params={"deleted_by": self.current_user})

    def get_tasks(self):
        return self._request("GET", "/tarefas")

    # ── Agenda ─────────────────────────────────────────────────────────────────

    def get_agenda(self, start, end):
        return self._request("GET", "/agenda", params={"start": start, "end": end})

    # ── Find ───────────────────────────────────────────────────────────────────

    def find_by_name(self, name):
        data, status = self._request("GET", f"/find/{name}")
        if status == 200:
            return data.get("item"), data.get("resource")
        return None, None

    # ── Historico ──────────────────────────────────────────────────────────────

    def get_history(self):
        return self._request("GET", "/historico")