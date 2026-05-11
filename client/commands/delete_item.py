from client.commands.base import ICommand


class DeleteItemCmd(ICommand):
    def __init__(self, proxy):
        self.proxy = proxy

    def execute(self):
        name = input("Nome do item a deletar: ")
        item, resource = self.proxy.find_by_name(name)

        if item is None:
            print(f"❌ Nenhum item encontrado com o nome '{name}'")
            return

        print(f"\n⚠️  Item encontrado: [{resource.upper()}] {item['title']}")
        confirm = input("Confirma a exclusão? (s/n): ").strip().lower()

        if confirm != "s":
            print("❌ Exclusão cancelada.")
            return

        if resource == "events":
            data, status = self.proxy.delete_event(name)
        elif resource == "tasks":
            data, status = self.proxy.delete_task(name)
        elif resource == "reminders":
            data, status = self.proxy.delete_reminder(name)

        if status == 200:
            print(f"✅ '{name}' deletado com sucesso!")
        else:
            print(f"❌ Erro: {data}")