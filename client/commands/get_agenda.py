from client.commands.base import ICommand


class GetAgendaCmd(ICommand):
    def __init__(self, proxy):
        self.proxy = proxy

    def execute(self):
        # primeiro mostra tudo
        data, status = self.proxy.get_agenda("2000-01-01", "2099-12-31")

        if status != 200:
            print(f"❌ Erro ao buscar agenda: {data}")
            return

        if not data:
            print("\n📅 Nenhum item cadastrado na agenda.")
            return

        self._print_agenda(data, "Agenda Completa")

        # pergunta se quer filtrar
        filtrar = input("\nDeseja filtrar por intervalo de datas? (s/n): ").strip().lower()
        if filtrar != "s":
            return

        start = input("Data inicial (YYYY-MM-DD): ").strip()
        end = input("Data final (YYYY-MM-DD): ").strip()

        data, status = self.proxy.get_agenda(start, end)

        if status != 200:
            print(f"❌ Erro ao filtrar agenda: {data}")
            return

        if not data:
            print("\n📅 Nenhum item encontrado neste intervalo.")
            return

        self._print_agenda(data, f"Agenda: {start} até {end}")

    def _print_agenda(self, data, title):
        print(f"\n{'='*50}")
        print(f"     📅 {title}")
        print(f"{'='*50}\n")

        for item in data:
            date = item.get("date") or item.get("datetime", "")[:10]
            description = item.get("description", "")
            desc_str = f" — {description}" if description else ""
            print(f"📌 {date} - [{item['type']}] {item['title']}{desc_str}")

        print(f"\n{'='*50}")
        print(f"{len(data)} item(s) encontrado(s)")
        print(f"{'='*50}")