from client.commands.base import ICommand


class GetAgendaCmd(ICommand):
    def __init__(self, proxy):
        self.proxy = proxy

    def execute(self):
        start = input("Data inicial (YYYY-MM-DD): ")
        end = input("Data final (YYYY-MM-DD): ")
        data, status = self.proxy.get_agenda(start, end)

        if status != 200:
            print(f"❌ Erro ao buscar agenda: {data}")
            return

        if not data:
            print("\n📅 Nenhum item encontrado neste intervalo.")
            return

        print(f"\n{'='*50}")
        print(f"     📅 Agenda: {start} até {end}")
        print(f"{'='*50}\n")

        for item in data:
            date = item.get("date") or item.get("datetime", "")[:10]
            description = item.get("description", "")
            desc_str = f" — {description}" if description else ""
            print(f"📌 {date} - [{item['type']}] {item['title']}{desc_str}")

        print(f"\n{'='*50}")
        print(f"{len(data)} item(s) encontrado(s)")
        print(f"{'='*50}")