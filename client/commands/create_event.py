from client.commands.base import ICommand


class CreateEventCmd(ICommand):
    def __init__(self, proxy):
        self.proxy = proxy

    def execute(self):
        title = input("Título do evento: ")
        date = input("Data (YYYY-MM-DD): ")
        description = input("Descrição: ")
        data, status = self.proxy.create_event(title, date, description)
        if status == 201:
            print(f"✅ Evento '{data['title']}' criado com sucesso!")
        else:
            print(f"❌ Erro ao criar evento: {data}")