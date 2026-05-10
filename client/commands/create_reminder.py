from client.commands.base import ICommand


class CreateReminderCmd(ICommand):
    def __init__(self, proxy):
        self.proxy = proxy

    def execute(self):
        title = input("Título do lembrete: ")
        datetime = input("Data e hora (YYYY-MM-DDTHH:MM:SS): ")
        data, status = self.proxy.create_reminder(title, datetime)
        if status == 201:
            print(f"✅ Lembrete '{data['title']}' criado com sucesso!")
        else:
            print(f"❌ Erro ao criar lembrete: {data}")