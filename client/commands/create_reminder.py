from client.commands.base import ICommand
from client import validators


class CreateReminderCmd(ICommand):
    def __init__(self, proxy):
        self.proxy = proxy

    def execute(self):
        title = input("Título do lembrete: ").strip()
        if not validators.validate_not_empty(title, "Título"):
            return
        if not validators.validate_max_length(title, "Título"):
            return

        dt_input = input("Data e hora (DD/MM/YYYY HH:MM): ").strip()
        dt = validators.parse_datetime(dt_input)
        if not dt:
            print("❌ Data/hora inválida! Use o formato DD/MM/YYYY HH:MM")
            return

        data, status = self.proxy.create_reminder(title, dt)
        if status == 201:
            print(f"✅ Lembrete '{data['title']}' criado com sucesso!")
        elif status == 409:
            print(f"⚠️  Já existe um item com o nome '{title}'!")
        else:
            print(f"❌ Erro ao criar lembrete: {data}")