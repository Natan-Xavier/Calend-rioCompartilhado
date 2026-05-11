from client.commands.base import ICommand
from client import validators


class AddTaskCmd(ICommand):
    def __init__(self, proxy):
        self.proxy = proxy

    def execute(self):
        title = input("Título da tarefa: ").strip()
        if not validators.validate_not_empty(title, "Título"):
            return
        if not validators.validate_max_length(title, "Título"):
            return

        description = input("Descrição: ").strip()
        if not validators.validate_not_empty(description, "Descrição"):
            return

        date_input = input("Data (DD/MM/YYYY): ").strip()
        date = validators.parse_date(date_input)
        if not date:
            print("❌ Data inválida! Use o formato DD/MM/YYYY")
            return

        data, status = self.proxy.add_task(title, description, date)
        if status == 201:
            print(f"✅ Tarefa '{data['title']}' criada com sucesso!")
        elif status == 409:
            print(f"⚠️  Já existe um item com o nome '{title}'!")
        else:
            print(f"❌ Erro ao criar tarefa: {data}")