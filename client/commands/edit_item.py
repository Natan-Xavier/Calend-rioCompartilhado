from client.commands.base import ICommand


class EditItemCmd(ICommand):
    def __init__(self, proxy):
        self.proxy = proxy

    def execute(self):
        print("\nO que deseja editar?")
        print("1. Evento")
        print("2. Tarefa")
        print("3. Lembrete")
        choice = input("Opção: ")

        name = input("Nome atual do item: ")
        print("Digite os campos a editar (deixe em branco para não alterar)")

        if choice == "1":
            title = input("Novo título: ")
            date = input("Nova data (YYYY-MM-DD): ")
            description = input("Nova descrição: ")
            data_to_update = {}
            if title: data_to_update["title"] = title
            if date: data_to_update["date"] = date
            if description: data_to_update["description"] = description
            data, status = self.proxy.edit_event(name, data_to_update)

        elif choice == "2":
            title = input("Novo título: ")
            description = input("Nova descrição: ")
            data_to_update = {}
            if title: data_to_update["title"] = title
            if description: data_to_update["description"] = description
            data, status = self.proxy.edit_task(name, data_to_update)

        elif choice == "3":
            title = input("Novo título: ")
            datetime = input("Nova data e hora (YYYY-MM-DDTHH:MM:SS): ")
            data_to_update = {}
            if title: data_to_update["title"] = title
            if datetime: data_to_update["datetime"] = datetime
            data, status = self.proxy.edit_reminder(name, data_to_update)

        else:
            print("❌ Opção inválida!")
            return

        if status == 200:
            print(f"✅ Item atualizado com sucesso!")
        else:
            print(f"❌ Erro: {data}")