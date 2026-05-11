from client.commands.base import ICommand


class EditItemCmd(ICommand):
    def __init__(self, proxy):
        self.proxy = proxy

    def execute(self):
        name = input("Nome do item a editar: ")
        item, resource = self.proxy.find_by_name(name)

        if item is None:
            print(f"❌ Nenhum item encontrado com o nome '{name}'")
            return

        print(f"\n✅ Item encontrado: [{resource.upper()}] {item['title']}")
        print("Digite os novos valores (Enter para manter o atual):\n")

        data_to_update = {}

        if resource == "events":
            title = input(f"Título [{item.get('title')}]: ").strip()
            date = input(f"Data [{item.get('date')}]: ").strip()
            description = input(f"Descrição [{item.get('description')}]: ").strip()
            if title: data_to_update["title"] = title
            if date: data_to_update["date"] = date
            if description: data_to_update["description"] = description
            data, status = self.proxy.edit_event(name, data_to_update)

        elif resource == "tasks":
            title = input(f"Título [{item.get('title')}]: ").strip()
            description = input(f"Descrição [{item.get('description')}]: ").strip()
            if title: data_to_update["title"] = title
            if description: data_to_update["description"] = description
            data, status = self.proxy.edit_task(name, data_to_update)

        elif resource == "reminders":
            title = input(f"Título [{item.get('title')}]: ").strip()
            datetime = input(f"Data e hora [{item.get('datetime')}]: ").strip()
            if title: data_to_update["title"] = title
            if datetime: data_to_update["datetime"] = datetime
            data, status = self.proxy.edit_reminder(name, data_to_update)

        if status == 200:
            print(f"\n✅ Item atualizado com sucesso!")
        else:
            print(f"\n❌ Erro: {data}")