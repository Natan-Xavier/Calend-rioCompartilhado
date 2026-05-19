import requests


class CalendarProxy:
    def __init__(self, base_url=None):
        if base_url is None:
            ip = input("IP do servidor (Enter para localhost): ").strip()
            if not ip:
                base_url = "http://127.0.0.1:5000"
            elif ip.startswith("http"):
                base_url = ip
            else:
                base_url = f"http://{ip}:5000"
        self.base_url     = base_url
        self.current_user = "Anônimo"
        print(f"🔗 Conectado a: {self.base_url}\n")

    def _request(self, method, endpoint, data=None, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, json=data, params=params)
            return response.json(), response.status_code
        except requests.exceptions.ConnectionError:
            print("❌ Erro: servidor não está rodando!")
            return None, 503

    # ── /usuarios ──────────────────────────────────────────
    def create_user(self, name, email):
        return self._request("POST", "/usuarios", {"name": name, "email": email})

    def get_users(self):
        return self._request("GET", "/usuarios")

    def delete_user(self, user_id):
        return self._request("DELETE", f"/usuarios/{user_id}")

    # ── /eventos ───────────────────────────────────────────
    def create_event(self, title, date, description):
        return self._request("POST", "/eventos", {
            "title": title, "date": date, "description": description,
            "created_by": self.current_user
        })

    def edit_event(self, name, data):
        return self._request("PUT", f"/eventos/{name}", data)

    def delete_event(self, name):
        return self._request("DELETE", f"/eventos/{name}")

    # ── /lembretes ─────────────────────────────────────────
    def create_reminder(self, title, datetime_str):
        return self._request("POST", "/lembretes", {
            "title": title, "datetime": datetime_str,
            "created_by": self.current_user
        })

    def edit_reminder(self, name, data):
        return self._request("PUT", f"/lembretes/{name}", data)

    def delete_reminder(self, name):
        return self._request("DELETE", f"/lembretes/{name}")

    # ── /tarefas ───────────────────────────────────────────
    def add_task(self, title, description, date):
        return self._request("POST", "/tarefas", {
            "title": title, "description": description, "date": date,
            "created_by": self.current_user
        })

    def edit_task(self, name, data):
        return self._request("PUT", f"/tarefas/{name}", data)

    def delete_task(self, name):
        return self._request("DELETE", f"/tarefas/{name}")

    def get_tasks(self):
        return self._request("GET", "/tarefas")

    # ── /agenda ────────────────────────────────────────────
    def get_agenda(self, start, end):
        return self._request("GET", "/agenda", params={"start": start, "end": end})

    # ── /find ──────────────────────────────────────────────
    def find_by_name(self, name):
        data, status = self._request("GET", f"/find/{name}")
        if status == 200:
            return data.get("item"), data.get("resource")
        return None, None