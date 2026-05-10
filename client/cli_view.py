from client.calendar_proxy import CalendarProxy
from client.commands.create_user import CreateUserCmd
from client.commands.create_event import CreateEventCmd
from client.commands.create_reminder import CreateReminderCmd
from client.commands.add_task import AddTaskCmd
from client.commands.edit_item import EditItemCmd
from client.commands.delete_item import DeleteItemCmd
from client.commands.get_agenda import GetAgendaCmd


class CLIView:
    def __init__(self):
        self.proxy = CalendarProxy()
        self.commands = {
            "1": GetAgendaCmd(self.proxy),
            "2": CreateEventCmd(self.proxy),
            "3": AddTaskCmd(self.proxy),
            "4": CreateReminderCmd(self.proxy),
            "5": EditItemCmd(self.proxy),
            "6": DeleteItemCmd(self.proxy),
            "7": CreateUserCmd(self.proxy),
        }

    def show_menu(self):
        print("\n" + "="*45)
        print("          📅 SharedCalendar")
        print("="*45)
        print("  1. Ver agenda (por intervalo de datas)")
        print("  2. Criar evento")
        print("  3. Criar tarefa")
        print("  4. Criar lembrete")
        print("  5. Editar item")
        print("  6. Deletar item")
        print("  7. Criar usuário")
        print("  0. Sair")
        print("="*45)

    def run(self):
        print("\n🚀 Bem-vindo ao SharedCalendar!")
        while True:
            self.show_menu()
            choice = input("\nEscolha uma opção: ").strip()

            if choice == "0":
                print("\n👋 Até logo!")
                break
            elif choice in self.commands:
                print()
                self.commands[choice].execute()
            else:
                print("❌ Opção inválida, tente novamente.")


if __name__ == "__main__":
    view = CLIView()
    view.run()