from client.commands.base import ICommand


class AddTaskCmd(ICommand):
    def __init__(self, proxy):
        self.proxy = proxy

    def execute(self):
        title = input("Título da tarefa: ")
        description = input("Descrição: ")
        data, status = self.proxy.add_task(title, description)
        if status == 201:
            print(f"✅ Tarefa '{data['title']}' criada com sucesso!")
        else:
            print(f"❌ Erro ao criar tarefa: {data}")