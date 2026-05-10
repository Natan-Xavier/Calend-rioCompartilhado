from client.commands.base import ICommand


class DeleteItemCmd(ICommand):
    def __init__(self, proxy):
        self.proxy = proxy

    def execute(self):
        print("\nO que deseja deletar?")
        print("1. Evento")
        print("2. Tarefa")
        print("3. Lembrete")
        choice = input("Opção: ")
        name = input("Nome do item: ")

        if choice == "1":
            data, status = self.proxy.delete_event(name)
        elif choice == "2":
            data, status = self.proxy.delete_task(name)
        elif choice == "3":
            data, status = self.proxy.delete_reminder(name)
        else:
            print("❌ Opção inválida!")
            return

        if status == 200:
            print(f"✅ '{name}' deletado com sucesso!")
        elif status == 404:
            print(f"❌ Item '{name}' não encontrado!")
        else:
            print(f"❌ Erro: {data}")