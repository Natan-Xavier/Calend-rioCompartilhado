import requests


class CalendarProxy:
    def __init__(self, base_url=None):
        if base_url is None:
            base_url = input("IP do servidor (Enter para localhost): ").strip()
            if not base_url:
                base_url = "http://127.0.0.1:5000"
            elif not base_url.startswith("http"):
                base_url = f"http://{base_url}:5000"
        self.base_url = base_url
        print(f"🔗 Conectado a: {self.base_url}\n")

    def _request(self, method, endpoint, data=None, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, json=data, params=params)
            return response.json(), response.status_code
        except requests.exceptions.ConnectionError:
            print("❌ Erro: servidor não está rodando!")
            return None, 503

    # ── /usuarios ──────────────────────────────────────
    def create_user(self, name, email):
        return self._request("POST", "/usuarios", {"name": name, "email": email})

    # ── /eventos ───────────────────────────────────────
    def create_event(self, title, date, description):
        return self._request("POST", "/eventos", {
            "title": title, "date": date, "description": description
        })

    def edit_event(self, name, data):
        return self._request("PUT", f"/eventos/{name}", data)

    def delete_event(self, name):
        return self._request("DELETE", f"/eventos/{name}")

    # ── /lembretes ─────────────────────────────────────
    def create_reminder(self, title, datetime):
        return self._request("POST", "/lembretes", {
            "title": title, "datetime": datetime
        })

    def edit_reminder(self, name, data):
        return self._request("PUT", f"/lembretes/{name}", data)

    def delete_reminder(self, name):
        return self._request("DELETE", f"/lembretes/{name}")

    # ── /tarefas ───────────────────────────────────────
    def add_task(self, title, description):
        return self._request("POST", "/tarefas", {
            "title": title, "description": description
        })

    def edit_task(self, name, data):
        return self._request("PUT", f"/tarefas/{name}", data)

    def delete_task(self, name):
        return self._request("DELETE", f"/tarefas/{name}")

    def get_tasks(self):
        return self._request("GET", "/tarefas")

    # ── /agenda ────────────────────────────────────────
    def get_agenda(self, start, end):
        return self._request("GET", "/agenda", params={"start": start, "end": end})