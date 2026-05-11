from client.commands.base import ICommand
from client import validators


class CreateEventCmd(ICommand):
    def __init__(self, proxy):
        self.proxy = proxy

    def execute(self):
        title = input("Título do evento: ").strip()
        if not validators.validate_not_empty(title, "Título"):
            return
        if not validators.validate_max_length(title, "Título"):
            return

        date_input = input("Data (DD/MM/YYYY): ").strip()
        date = validators.parse_date(date_input)
        if not date:
            print("❌ Data inválida! Use o formato DD/MM/YYYY")
            return

        description = input("Descrição: ").strip()
        if not validators.validate_not_empty(description, "Descrição"):
            return

        data, status = self.proxy.create_event(title, date, description)
        if status == 201:
            print(f"✅ Evento '{data['title']}' criado com sucesso!")
        elif status == 409:
            print(f"⚠️  Já existe um item com o nome '{title}'!")
        else:
            print(f"❌ Erro ao criar evento: {data}")