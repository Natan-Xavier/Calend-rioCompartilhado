from client.commands.base import ICommand
from client import validators


class GetAgendaCmd(ICommand):
    def __init__(self, proxy):
        self.proxy = proxy

    def execute(self):
        data, status = self.proxy.get_agenda("2000-01-01", "2099-12-31")

        if status != 200:
            print(f"❌ Erro ao buscar agenda: {data}")
            return

        if not data:
            print("\n📅 Nenhum item cadastrado na agenda.")
            return

        self._print_agenda(data, "Agenda Completa")

        filtrar = input("\nDeseja filtrar por intervalo de datas? (s/n): ").strip().lower()
        if filtrar != "s":
            return

        start_input = input("Data inicial (DD/MM/YYYY): ").strip()
        start = validators.parse_date(start_input)
        if not start:
            print("❌ Data inválida! Use o formato DD/MM/YYYY")
            return

        end_input = input("Data final (DD/MM/YYYY): ").strip()
        end = validators.parse_date(end_input)
        if not end:
            print("❌ Data inválida! Use o formato DD/MM/YYYY")
            return

        if end < start:
            print("❌ Data final não pode ser anterior à data inicial!")
            return

        data, status = self.proxy.get_agenda(start, end)

        if status != 200:
            print(f"❌ Erro ao filtrar agenda: {data}")
            return

        if not data:
            print("\n📅 Nenhum item encontrado neste intervalo.")
            return

        self._print_agenda(data, f"Agenda: {validators.format_display_date(start)} até {validators.format_display_date(end)}")

    def _print_agenda(self, data, title):
        print(f"\n{'='*50}")
        print(f"     📅 {title}")
        print(f"{'='*50}\n")

        for item in data:
            if item.get("datetime"):
                date = validators.format_display_date(item["datetime"][:10])
                time = item["datetime"][11:16]
                date_str = f"{date} {time}"
            else:
                date_str = validators.format_display_date(item.get("date", ""))

            description = item.get("description", "")
            desc_str = f" — {description}" if description else ""
            icon = "🔔" if item["type"] == "LEMBRETE" else "📌"
            print(f"{icon} {date_str} - [{item['type']}] {item['title']}{desc_str}")

        print(f"\n{'='*50}")
        print(f"{len(data)} item(s) encontrado(s)")
        print(f"{'='*50}")